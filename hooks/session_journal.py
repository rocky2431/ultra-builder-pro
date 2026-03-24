#!/usr/bin/env python3
"""Session Journal Hook - Stop

Records session events to SQLite + JSONL for cross-session memory.
Identity: uses content_session_id from hook protocol; merge window as fallback.

Layer 2: AI-generated structured summary via Haiku (non-blocking daemon).
Layer 2 fallback: Git commit messages as summary.

Execution target: < 100ms (daemon spawns async, no blocking in hot path).
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import shared memory_db module
sys.path.insert(0, str(Path(__file__).parent))
import memory_db

GIT_TIMEOUT = 3
COMMIT_WINDOW_MIN = 30
AI_SUMMARIZE_DELAY = 10
TRANSCRIPT_HEAD_CHARS = 4000   # First N chars: problem context & initial decisions
TRANSCRIPT_TAIL_CHARS = 11000  # Last N chars: resolution & recent work
TRANSCRIPT_MAX_CHARS = 15000   # Total budget (head + tail)
TRANSCRIPT_MAX_MESSAGES = 100  # Increased from 50 for better coverage
AI_MODEL_CLI = "haiku"
AI_MAX_TOKENS = 1000


def _get_daemon_log() -> Path:
    """Get project-scoped daemon error log path."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()) / ".ultra" / "memory" / "daemon-errors.log"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.home() / ".claude" / "memory" / "daemon-errors.log"

# Allowed parent directories for transcript files
ALLOWED_TRANSCRIPT_DIRS = [
    Path.home() / ".claude",
    Path("/tmp"),
    Path("/private/tmp"),
]

# Env vars allowed in AI summarize daemon (whitelist > blacklist for security)
DAEMON_ENV_WHITELIST = {
    "PATH", "HOME", "USER", "SHELL", "LANG", "LC_ALL", "LC_CTYPE",
    "TMPDIR", "TERM", "LOGNAME", "XDG_RUNTIME_DIR",
}


def _validate_transcript_path(transcript_path: str) -> bool:
    """Validate transcript path is under an allowed directory."""
    try:
        resolved = Path(transcript_path).resolve()
        return any(
            str(resolved).startswith(str(d.resolve()))
            for d in ALLOWED_TRANSCRIPT_DIRS
        )
    except (OSError, ValueError):
        return False


def run_git(*args) -> str:
    """Run git command, return stdout or empty string."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.rstrip('\n')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def get_modified_files() -> list:
    """Get list of modified/staged files from git status."""
    status = run_git("status", "--porcelain")
    if not status:
        return []

    files = []
    for line in status.split("\n"):
        if not line or len(line) < 4:
            continue
        filepath = line[3:].strip()
        if " -> " in filepath:
            filepath = filepath.split(" -> ")[1]
        files.append(filepath)

    return files


def get_recent_commits() -> str:
    """Extract recent commit messages as fallback summary."""
    log = run_git(
        "log", "--oneline",
        f"--since={COMMIT_WINDOW_MIN} minutes ago",
        "--no-merges",
        "--format=%s"
    )
    if not log:
        return ""

    messages = log.split("\n")
    seen = set()
    unique = []
    for msg in messages:
        msg = msg.strip()
        if msg and msg not in seen:
            seen.add(msg)
            unique.append(msg)

    if not unique:
        return ""

    summary = " + ".join(unique)
    if len(summary) > 200:
        summary = summary[:197] + "..."

    return summary


# -- Transcript Parsing & AI Summarization --


def parse_hook_input(raw: str) -> dict:
    """Parse stdin JSON from hook protocol.

    Returns dict with transcript_path and session metadata, or empty dict.
    """
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw.strip())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def extract_transcript_text(transcript_path: str) -> str:
    """Extract meaningful user/assistant conversation from JSONL transcript.

    Uses Head + Tail sampling to preserve both:
    - Beginning: problem context, initial requirements, key decisions
    - End: resolution, final state, recent work

    Skips tool_use, thinking, progress, and file-history-snapshot entries.
    Returns truncated text suitable for AI summarization.
    """
    if not _validate_transcript_path(transcript_path):
        return ""

    path = Path(transcript_path)
    if not path.exists():
        return ""

    messages = []
    seen_texts = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type")
                if entry_type not in ("user", "assistant"):
                    continue

                msg = entry.get("message", {})
                role = msg.get("role", "")
                content = msg.get("content", "")

                text = ""
                if isinstance(content, str):
                    text = content.strip()
                elif isinstance(content, list):
                    parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            t = item.get("text", "").strip()
                            if t:
                                parts.append(t)
                    text = " ".join(parts)

                # Skip very short fragments and duplicates (streaming chunks)
                if text and len(text) > 10 and text not in seen_texts:
                    seen_texts.add(text)
                    messages.append(f"{role}: {text}")
    except OSError:
        return ""

    if not messages:
        return ""

    # Cap total message count
    if len(messages) > TRANSCRIPT_MAX_MESSAGES:
        messages = messages[:TRANSCRIPT_MAX_MESSAGES]

    full_text = "\n".join(messages)

    # If within budget, return as-is
    if len(full_text) <= TRANSCRIPT_MAX_CHARS:
        return full_text

    # Head + Tail sampling: keep beginning (problem context) + end (resolution)
    head_text = "\n".join(messages)
    head_part = head_text[:TRANSCRIPT_HEAD_CHARS]
    # Snap to newline boundary
    nl = head_part.rfind("\n")
    if nl > TRANSCRIPT_HEAD_CHARS // 2:
        head_part = head_part[:nl]

    tail_part = head_text[-TRANSCRIPT_TAIL_CHARS:]
    # Snap to newline boundary
    nl = tail_part.find("\n")
    if 0 < nl < 200:
        tail_part = tail_part[nl + 1:]

    # Check for overlap (short sessions)
    if len(head_part) + len(tail_part) >= len(full_text):
        return full_text

    return (
        head_part
        + "\n\n[... middle of session omitted ...]\n\n"
        + tail_part
    )


def spawn_ai_summarize(session_id: str, transcript_path: str,
                       db_path: str) -> None:
    """Spawn a double-fork daemon for non-blocking AI summarization.

    Parent returns immediately (<1ms). Daemon waits AI_SUMMARIZE_DELAY
    seconds, generates structured summary via Haiku, writes to DB + Chroma.
    """
    try:
        pid = os.fork()
    except OSError:
        return

    if pid > 0:
        os.waitpid(pid, 0)
        return

    # First child: new session, fork again
    try:
        os.setsid()
    except OSError:
        pass

    try:
        pid2 = os.fork()
    except OSError:
        os._exit(1)

    if pid2 > 0:
        os._exit(0)

    # Grandchild (daemon): detach stdio
    try:
        devnull = os.open(os.devnull, os.O_RDWR)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        if devnull > 2:
            os.close(devnull)
    except OSError:
        pass

    try:
        _run_ai_summarize(session_id, transcript_path, db_path)
    except Exception:
        _log_daemon_error()

    os._exit(0)


def _log_daemon_error() -> None:
    """Write daemon exception to log file (stdio is /dev/null)."""
    import traceback
    try:
        log_path = _get_daemon_log()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} "
                    f"{traceback.format_exc()}\n")
    except OSError:
        pass


def _run_ai_summarize(session_id: str, transcript_path: str,
                      db_path: str) -> None:
    """Daemon main: wait, extract transcript, summarize via Haiku, store structured.

    Output: JSON with request/completed/learned/next_steps fields.
    Storage: session_summaries table (structured) + sessions.summary (legacy compat).
    """
    import time
    time.sleep(AI_SUMMARIZE_DELAY)

    text = extract_transcript_text(transcript_path)
    if not text:
        return

    prompt = (
        "Summarize this Claude Code session as JSON. "
        "Output ONLY valid JSON, no markdown fences, no preamble.\n\n"
        "Schema:\n"
        '{"request": "what the user asked for (1-2 sentences)",'
        ' "completed": "what was built/fixed/completed (2-5 bullets, pipe-separated)",'
        ' "learned": "key decisions, insights, and gotchas (1-3 bullets, pipe-separated, empty string if none)",'
        ' "next_steps": "pending work or follow-ups (1-3 bullets, pipe-separated, empty string if none)"}\n\n'
        "Rules:\n"
        "- Each bullet max 30 words\n"
        "- CRITICAL: Include specific file names (e.g. auth.ts, memory_db.py) in completed AND learned fields\n"
        "- In 'learned', mention which file the lesson applies to (e.g. 'validate token in auth.ts before decode')\n"
        "- In 'completed', list each file created or modified by name\n"
        "- Include function names and error messages when relevant\n"
        "- Use | as bullet separator within each field\n"
        "- Empty string for fields with nothing to report\n\n"
        f"Session transcript:\n{text}"
    )

    # SDK fallback removed: ANTHROPIC_API_KEY is stripped by DAEMON_ENV_WHITELIST,
    # so _try_anthropic_sdk would never succeed in the daemon context.
    raw = _try_claude_cli(prompt)
    if not raw:
        return

    # Parse structured JSON response
    parsed = _parse_summary_json(raw)
    if not parsed:
        return

    # Store in DB
    try:
        conn = memory_db.init_db(Path(db_path))

        # Race-condition guard: check structured summary table
        existing = conn.execute(
            "SELECT status FROM session_summaries WHERE session_id = ?",
            (session_id,)
        ).fetchone()
        if existing and existing["status"] == "ready":
            conn.close()
            return

        saved = memory_db.save_structured_summary(
            conn, session_id,
            request=parsed["request"],
            completed=parsed["completed"],
            learned=parsed["learned"],
            next_steps=parsed["next_steps"],
            source="model",
            model=AI_MODEL_CLI,
        )

        if saved:
            # Build legacy summary text for Chroma embedding
            legacy = parsed["completed"]
            if parsed["learned"]:
                legacy += " | " + parsed["learned"]

            row = conn.execute(
                "SELECT branch, files_modified FROM sessions WHERE id = ?",
                (session_id,)
            ).fetchone()
            if row:
                files = json.loads(row["files_modified"])
                memory_db.upsert_embedding(
                    session_id, legacy, row["branch"], files
                )
        conn.close()
    except Exception:
        _log_daemon_error()


def _parse_summary_json(raw: str) -> dict | None:
    """Parse AI summary response as JSON. Handles markdown fences and whitespace."""
    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        first_nl = text.find("\n")
        if first_nl > 0:
            text = text[first_nl + 1:]
        if text.endswith("```"):
            text = text[:-3].rstrip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from surrounding text
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
        else:
            return None

    if not isinstance(data, dict):
        return None

    # Extract fields with defaults
    result = {
        "request": str(data.get("request", "")).strip(),
        "completed": str(data.get("completed", "")).strip(),
        "learned": str(data.get("learned", "")).strip(),
        "next_steps": str(data.get("next_steps", "")).strip(),
    }

    # Validate: must have at least request + completed with meaningful content
    total = len(result["request"]) + len(result["completed"])
    if total < 20:
        return None

    return result


def _try_claude_cli(prompt: str) -> str:
    """Tier 1: claude -p --model haiku --no-session-persistence.

    Uses Claude Code's existing OAuth auth (Max subscription).
    --no-session-persistence prevents polluting /resume with summary sessions.
    Clears CLAUDE* env vars to avoid nesting detection, and removes
    ANTHROPIC_API_KEY to force OAuth fallback (the env var may contain
    a placeholder that causes 401 errors).
    """
    try:
        env = {k: v for k, v in os.environ.items()
               if k in DAEMON_ENV_WHITELIST}
        env.setdefault("PATH", "/usr/bin:/usr/local/bin")
        env["ULTRA_AI_DAEMON"] = "1"

        result = subprocess.run(
            ["claude", "-p", "--model", AI_MODEL_CLI,
             "--no-session-persistence", prompt],
            capture_output=True, text=True, timeout=60, env=env
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if len(output) > 20:
                return output
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return ""


# -- Main Entry Points --


def main():
    # Parse stdin (hook protocol may include transcript_path)
    raw_input = ""
    try:
        raw_input = sys.stdin.read()
    except Exception:
        pass

    hook_data = parse_hook_input(raw_input)

    # Skip when running inside AI summarize daemon (prevents ghost sessions)
    if os.environ.get("ULTRA_AI_DAEMON") == "1":
        print(json.dumps({}))
        return

    # v2: skip DB write entirely on re-trigger (root cause of stop_count=4306)
    is_retrigger = hook_data.get("stop_hook_active", False)
    if is_retrigger:
        print(json.dumps({}))
        return

    # v2: use real session_id from hook protocol
    content_session_id = hook_data.get("session_id", "")
    transcript_path = hook_data.get("transcript_path", "")

    # Get branch (fallback to "unknown" for detached HEAD / edge cases)
    branch = run_git("branch", "--show-current")
    if not branch:
        # Try HEAD ref as fallback (detached HEAD, tags, etc.)
        branch = run_git("rev-parse", "--short", "HEAD") or "unknown"

    cwd = os.getcwd()
    files_modified = get_modified_files()

    # Fallback summary from git commits
    auto_summary = get_recent_commits()

    # Write to SQLite (v2: use content_session_id if available)
    session_id = None
    has_existing_summary = False
    db_path = str(memory_db.get_db_path())
    try:
        conn = memory_db.init_db()
        session_id = memory_db.upsert_session(
            conn, branch, cwd, files_modified,
            content_session_id=content_session_id
        )

        # Check if session already has a structured or legacy summary
        if session_id:
            row = conn.execute(
                "SELECT summary FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if row and row["summary"] and len(row["summary"]) > 100:
                has_existing_summary = True
            # Also check structured summaries
            try:
                ss = conn.execute(
                    "SELECT status FROM session_summaries WHERE session_id = ?",
                    (session_id,)
                ).fetchone()
                if ss and ss["status"] == "ready":
                    has_existing_summary = True
            except Exception:
                pass

        # Fill commit-based summary as fallback (only if no summary yet)
        if auto_summary and session_id and not has_existing_summary:
            memory_db.update_summary(conn, session_id, auto_summary)

        conn.close()
    except Exception:
        print("[session_journal] DB write failed", file=sys.stderr)

    # Spawn AI summarize daemon only if no existing summary
    if transcript_path and session_id and not has_existing_summary:
        spawn_ai_summarize(session_id, transcript_path, db_path)

    # Append to JSONL (backup)
    try:
        jsonl_path = memory_db.get_jsonl_path()
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "sid": session_id,
            "content_sid": content_session_id,
            "branch": branch,
            "cwd": cwd,
            "files": files_modified,
            "auto_summary": auto_summary,
            "has_transcript": bool(transcript_path),
        }
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[session_journal] JSONL error: {e}", file=sys.stderr)

    print(json.dumps({}))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ai-summarize":
        if len(sys.argv) < 4:
            print("Usage: session_journal.py --ai-summarize "
                  "<session_id> <transcript_path>")
            sys.exit(1)
        sid = sys.argv[2]
        tp = sys.argv[3]
        db = str(memory_db.get_db_path())
        print(f"Generating AI summary for session {sid}...")
        _run_ai_summarize(sid, tp, db)
        conn = memory_db.init_db()
        # Check structured summary first, then legacy
        ss = conn.execute(
            "SELECT status, request, completed, learned, next_steps "
            "FROM session_summaries WHERE session_id = ?", (sid,)
        ).fetchone()
        if ss and ss["status"] == "ready":
            print(f"Structured summary generated:")
            print(f"  Request: {ss['request']}")
            print(f"  Completed: {ss['completed']}")
            print(f"  Learned: {ss['learned']}")
            print(f"  Next steps: {ss['next_steps']}")
        else:
            result = conn.execute(
                "SELECT summary FROM sessions WHERE id = ?", (sid,)
            ).fetchone()
            if result and result["summary"]:
                print(f"Legacy summary:\n{result['summary']}")
            else:
                print("No summary generated (check transcript path and API access)")
        conn.close()
    else:
        main()
