#!/usr/bin/env python3
"""Session Journal Hook - Stop

Records session events to SQLite + JSONL for cross-session memory.
Debounced: merges entries within 30-minute windows for same branch+cwd.

Layer 2: AI-generated summary from transcript via Haiku (non-blocking daemon).
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
TRANSCRIPT_MAX_CHARS = 8000
TRANSCRIPT_MAX_MESSAGES = 50


def run_git(*args) -> str:
    """Run git command, return stdout or empty string."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
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

    Skips tool_use, thinking, progress, and file-history-snapshot entries.
    Returns truncated text suitable for AI summarization (~2000 tokens).
    """
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

    recent = messages[-TRANSCRIPT_MAX_MESSAGES:]
    result = "\n".join(recent)

    if len(result) > TRANSCRIPT_MAX_CHARS:
        result = result[-TRANSCRIPT_MAX_CHARS:]
        nl = result.find("\n")
        if 0 < nl < 200:
            result = result[nl + 1:]

    return result


def spawn_ai_summarize(session_id: str, transcript_path: str,
                       db_path: str, cwd: str) -> None:
    """Spawn a double-fork daemon for non-blocking AI summarization.

    Parent returns immediately (<1ms). Daemon waits AI_SUMMARIZE_DELAY
    seconds, generates summary via Haiku, writes to DB + Chroma.
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
        _run_ai_summarize(session_id, transcript_path, db_path, cwd)
    except Exception:
        pass

    os._exit(0)


def _run_ai_summarize(session_id: str, transcript_path: str,
                      db_path: str, _cwd: str = "") -> None:
    """Daemon main: wait, extract transcript, summarize, update DB + Chroma."""
    import time
    time.sleep(AI_SUMMARIZE_DELAY)

    text = extract_transcript_text(transcript_path)
    if not text:
        return

    prompt = (
        "Summarize this Claude Code session in 3-8 bullet points. "
        "Focus on: what was accomplished, key decisions made, problems encountered. "
        "Keep each bullet under 20 words. Output ONLY the bullet list, no preamble.\n\n"
        f"Session transcript:\n{text}"
    )

    summary = _try_claude_cli(prompt) or _try_anthropic_sdk(prompt)
    if not summary:
        return

    # Update SQLite + Chroma
    try:
        conn = memory_db.init_db(Path(db_path))
        memory_db.update_summary(conn, session_id, summary)

        row = conn.execute(
            "SELECT branch, files_modified FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        if row:
            files = json.loads(row["files_modified"])
            memory_db.upsert_embedding(
                session_id, summary, row["branch"], files
            )
        conn.close()
    except Exception:
        pass


def _try_claude_cli(prompt: str) -> str:
    """Tier 1: claude -p --model haiku. Clears CLAUDE* env vars."""
    try:
        env = {k: v for k, v in os.environ.items()
               if not k.startswith("CLAUDE")}
        env["PATH"] = os.environ.get("PATH", "/usr/bin:/usr/local/bin")

        result = subprocess.run(
            ["claude", "-p", "--model", "haiku", prompt],
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if len(output) > 20:
                return output
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return ""


def _try_anthropic_sdk(prompt: str) -> str:
    """Tier 2: Anthropic SDK direct call. Requires ANTHROPIC_API_KEY."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        if response.content:
            block = response.content[0]
            if block.type == "text":
                text = block.text.strip()
                if len(text) > 20:
                    return text
    except Exception:
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
    transcript_path = hook_data.get("transcript_path", "")

    # Must be in a git repo
    branch = run_git("branch", "--show-current")
    if not branch:
        print(json.dumps({}))
        return

    cwd = os.getcwd()
    files_modified = get_modified_files()

    # Fallback summary from git commits
    auto_summary = get_recent_commits()

    # Write to SQLite (with 30-min merge window)
    session_id = None
    db_path = str(memory_db.get_db_path())
    try:
        conn = memory_db.init_db()
        session_id = memory_db.upsert_session(
            conn, branch, cwd, files_modified
        )

        # Fill commit-based summary as fallback (AI daemon overwrites later)
        if auto_summary and session_id:
            current = memory_db.get_latest(conn)
            if current and not current.get("summary"):
                memory_db.update_summary(conn, session_id, auto_summary)

        conn.close()
    except Exception as e:
        print(f"[session_journal] DB error: {e}", file=sys.stderr)

    # Spawn AI summarize daemon (non-blocking, overwrites commit summary)
    if transcript_path and session_id:
        spawn_ai_summarize(session_id, transcript_path, db_path, cwd)

    # Append to JSONL (backup)
    try:
        jsonl_path = memory_db.get_jsonl_path()
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "sid": session_id,
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
        _run_ai_summarize(sid, tp, db, os.getcwd())
        conn = memory_db.init_db()
        result = conn.execute(
            "SELECT summary FROM sessions WHERE id = ?", (sid,)
        ).fetchone()
        conn.close()
        if result and result["summary"]:
            print(f"Summary generated:\n{result['summary']}")
        else:
            print("No summary generated (check transcript path and API access)")
    else:
        main()
