#!/usr/bin/env python3
"""
Pre-Stop Check Hook - Stop
Checks for unreviewed code changes before session ends.

Three-layer check with session-scoped circuit breaker:
0. Circuit breaker: If blocked >= MAX_STOP_BLOCKS times in this session → allow stop
1. Review artifacts: If a recent (<2h) ultra-review session exists:
   - P0/P1 unresolved (REQUEST_CHANGES) → block
   - APPROVE/COMMENT → allow stop
   - Incomplete + < 15min old → warn only (agents may still be running)
   - Incomplete + >= 15min old → block
2. Code changes (fallback): If no recent review session:
   - Code files changed but not reviewed → block + suggest running code-reviewer
3. Security-sensitive file detection: auth/payment/token files → MANDATORY review reminder

Uses last_assistant_message to detect incomplete work patterns.

Counter file: /tmp/.claude_stop_count_<session_id>
Old counter files (>24h) are cleaned up automatically.
"""

import sys
import json
import subprocess
import os
import hashlib
import tempfile
import time
import glob as glob_module
from pathlib import Path


STOP_COUNT_PREFIX = ".claude_stop_count_"
MAX_STOP_BLOCKS = 2  # Block at most 2 times, then allow stop
GIT_TIMEOUT = 3  # seconds (must be < hook timeout of 5s)
COUNTER_MAX_AGE = 86400  # 24 hours
INCOMPLETE_GRACE_PERIOD = 900  # 15 min - agents may still be running
SESSION_MAX_AGE = 7200  # 2 hours - only consider recent review sessions

SECURITY_PATTERNS = {'auth', 'login', 'password', 'payment', 'secret', 'token', 'credential', 'session'}
INCOMPLETE_WORK_PATTERNS = ['todo', 'fixme', 'hack', 'unfinished', 'not yet', 'wip', 'work in progress']


# -- Circuit Breaker (session-scoped counter) --


def cleanup_old_counters() -> None:
    """Remove counter files older than COUNTER_MAX_AGE seconds."""
    try:
        tmp_dir = tempfile.gettempdir()
        now = time.time()
        pattern = os.path.join(tmp_dir, f"{STOP_COUNT_PREFIX}*")
        for path in glob_module.glob(pattern):
            try:
                if now - os.path.getmtime(path) > COUNTER_MAX_AGE:
                    os.unlink(path)
            except OSError:
                pass
    except Exception:
        pass


def get_stop_count_path(session_id: str) -> str:
    """Get the counter file path for a session."""
    return os.path.join(tempfile.gettempdir(), f"{STOP_COUNT_PREFIX}{session_id}")


def get_stop_count(session_id: str) -> int:
    """Read current block count for this session."""
    try:
        with open(get_stop_count_path(session_id)) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def increment_stop_count(session_id: str) -> int:
    """Increment and return block count for this session."""
    count = get_stop_count(session_id) + 1
    path = get_stop_count_path(session_id)
    try:
        with open(path, 'w') as f:
            f.write(str(count))
        os.chmod(path, 0o600)
    except OSError:
        pass
    return count


# -- Git Helpers --


def get_git_status() -> dict:
    """Get current git status."""
    result = {
        'has_changes': False,
        'staged': [],
        'unstaged': [],
        'untracked': []
    }

    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True, text=True,
            cwd=os.getcwd(), timeout=GIT_TIMEOUT
        )
        if proc.returncode != 0:
            print("[pre_stop_check] Not in a git repo, skipping", file=sys.stderr)
            return result

        proc = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True,
            cwd=os.getcwd(), timeout=GIT_TIMEOUT
        )

        if proc.returncode != 0:
            print(f"[pre_stop_check] git status failed: {proc.stderr.strip()}", file=sys.stderr)
            return result

        for line in proc.stdout.rstrip('\n').split('\n'):
            if not line:
                continue

            status = line[:2]
            filepath = line[3:]

            if status[0] in 'MADRC':
                result['staged'].append(filepath)
            if status[1] in 'MD':
                result['unstaged'].append(filepath)
            if status == '??':
                result['untracked'].append(filepath)

        result['has_changes'] = bool(result['staged'] or result['unstaged'])

    except subprocess.TimeoutExpired:
        print("[pre_stop_check] git command timed out, allowing stop", file=sys.stderr)
    except Exception as e:
        print(f"[pre_stop_check] Error checking git status: {e}", file=sys.stderr)

    return result


def get_code_files(files: list) -> list:
    """Filter to code files only (excludes .md and other non-code files)."""
    code_extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.sol', '.rb', '.vue', '.svelte', '.css', '.scss', '.html', '.json', '.yaml', '.yml', '.toml', '.sh'}
    return [f for f in files if os.path.splitext(f)[1].lower() in code_extensions]


def get_changes_hash(files: list) -> str:
    """Generate a hash based on the set of changed files."""
    content = "\n".join(sorted(files))
    return hashlib.md5(content.encode()).hexdigest()[:12]


def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        proc = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True,
            cwd=os.getcwd(), timeout=GIT_TIMEOUT
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (subprocess.TimeoutExpired, Exception):
        return ""


# -- Review Artifact Checks --


def get_project_reviews_dir() -> Path | None:
    """Get the project-level reviews directory (.ultra/reviews/ relative to git toplevel).

    Returns None if not in a git repository (safe fallback — skip review checks).
    """
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True,
            cwd=os.getcwd(), timeout=GIT_TIMEOUT
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip()) / ".ultra" / "reviews"
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


def check_review_artifacts(branch: str = "") -> dict:
    """Check if a recent ultra-review session for the current branch has unresolved issues.

    Uses index.json (branch-scoped) with fallback to directory scan (time-scoped).

    Returns:
        dict with 'needs_review' (bool), optionally 'reason' (str),
        and 'review_passed' (bool) if a recent passing review exists.
    """
    maybe_reviews_dir = get_project_reviews_dir()
    if maybe_reviews_dir is None or not maybe_reviews_dir.exists():
        return {'needs_review': False, 'review_passed': False}
    reviews_dir: Path = maybe_reviews_dir

    current_branch = branch or get_current_branch()

    # Strategy 1: Use index.json (preferred — branch-scoped)
    index_file = reviews_dir / "index.json"
    if index_file.exists():
        try:
            index_data = json.loads(index_file.read_text())
            sessions = index_data.get('sessions', [])

            # Filter by current branch, sort by timestamp descending
            branch_sessions = [
                s for s in sessions
                if s.get('branch') == current_branch
            ] if current_branch else sessions

            if branch_sessions:
                latest = sorted(branch_sessions, key=lambda s: s.get('timestamp', ''), reverse=True)[0]
                session_dir = reviews_dir / latest['id']
                session_id = latest['id']

                # Recency check
                try:
                    if session_dir.exists() and time.time() - session_dir.stat().st_mtime > SESSION_MAX_AGE:
                        return {'needs_review': False, 'review_passed': False}
                except OSError:
                    pass

                verdict = latest.get('verdict')
                p0_count = latest.get('p0', 0)

                # Incomplete: coordinator hasn't set verdict yet
                if verdict is None or verdict == 'pending':
                    return {
                        'needs_review': False,
                        'review_passed': False,
                        'warn': f"Review session {session_id} still pending (no verdict yet)"
                    }

                if verdict == 'REQUEST_CHANGES' and p0_count > 0:
                    return {
                        'needs_review': True,
                        'review_passed': False,
                        'reason': f"Review found {p0_count} P0 critical issue(s) - fix before stopping"
                    }

                if verdict == 'REQUEST_CHANGES':
                    return {
                        'needs_review': True,
                        'review_passed': False,
                        'reason': "Review verdict is REQUEST_CHANGES (P1 issues unresolved)"
                    }

                if verdict in ('APPROVE', 'COMMENT'):
                    return {'needs_review': False, 'review_passed': True}

        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"[pre_stop_check] Failed to read index.json: {e}", file=sys.stderr)
            # Fall through to directory scan

    # Strategy 2: Fallback — scan directories (time-scoped, no branch filter)
    sessions = sorted(
        [d for d in reviews_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name, reverse=True
    )
    if not sessions:
        return {'needs_review': False, 'review_passed': False}

    latest = sessions[0]

    # Only consider recent sessions (within SESSION_MAX_AGE)
    try:
        session_age = time.time() - latest.stat().st_mtime
        if session_age > SESSION_MAX_AGE:
            return {'needs_review': False, 'review_passed': False}
    except OSError:
        return {'needs_review': False, 'review_passed': False}

    summary_json = latest / "SUMMARY.json"

    if not summary_json.exists():
        review_files = list(latest.glob("review-*.json"))
        if review_files:
            # Grace period: agents may still be running
            if session_age < INCOMPLETE_GRACE_PERIOD:
                return {
                    'needs_review': False,
                    'review_passed': False,
                    'warn': f"Review session {latest.name} in progress ({len(review_files)} agents done so far)"
                }
            # Abandoned
            return {
                'needs_review': True,
                'review_passed': False,
                'reason': f"Review session {latest.name} incomplete ({len(review_files)}/6 agents) - run review-coordinator or delete session"
            }
        return {'needs_review': False, 'review_passed': False}

    try:
        data = json.loads(summary_json.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"[pre_stop_check] Failed to read SUMMARY.json: {e}", file=sys.stderr)
        return {'needs_review': False, 'review_passed': False}

    verdict = data.get('verdict', 'APPROVE')
    p0_count = data.get('summary', {}).get('by_severity', {}).get('P0', 0)

    if verdict == 'REQUEST_CHANGES' and p0_count > 0:
        return {
            'needs_review': True,
            'review_passed': False,
            'reason': f"Review found {p0_count} P0 critical issue(s) - fix before stopping"
        }

    if verdict == 'REQUEST_CHANGES':
        return {
            'needs_review': True,
            'review_passed': False,
            'reason': "Review verdict is REQUEST_CHANGES (P1 issues unresolved)"
        }

    return {'needs_review': False, 'review_passed': True}


# -- Detection Helpers --


def detect_security_files(files: list) -> list:
    """Detect security-sensitive files from changed file list."""
    return [f for f in files
            if any(p in f.lower() for p in SECURITY_PATTERNS)]


def check_incomplete_work(last_message: str) -> bool:
    """Check if last assistant message suggests incomplete work."""
    if not last_message:
        return False
    lower = last_message.lower()
    return any(p in lower for p in INCOMPLETE_WORK_PATTERNS)


# -- Main --


def block_stop(session_id: str, reason: str) -> None:
    """Block stop: increment counter and output block decision."""
    if session_id:
        count = increment_stop_count(session_id)
        print(f"[pre_stop_check] Block #{count}/{MAX_STOP_BLOCKS}", file=sys.stderr)
    result = {
        "decision": "block",
        "reason": reason
    }
    print(json.dumps(result))


def main():
    try:
        input_data = sys.stdin.read()
        hook_data = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[pre_stop_check] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    session_id = hook_data.get("session_id", "")
    last_message = hook_data.get("last_assistant_message", "")

    cleanup_old_counters()

    # Layer 0a: Protocol fast path — stop_hook_active means Claude already continued once
    if hook_data.get("stop_hook_active", False):
        print("[pre_stop_check] stop_hook_active=true, allowing stop", file=sys.stderr)
        print(json.dumps({}))
        return

    # Layer 0b: Circuit breaker — max blocks reached → allow stop (prevent infinite loop)
    if session_id:
        stop_count = get_stop_count(session_id)
        if stop_count >= MAX_STOP_BLOCKS:
            print(f"[pre_stop_check] Circuit breaker: {stop_count}/{MAX_STOP_BLOCKS} blocks reached, allowing stop", file=sys.stderr)
            print(json.dumps({}))
            return

    # Get branch once, reuse across layers (saves ~30ms subprocess call)
    current_branch = get_current_branch()

    # Layer 1: Check review artifacts (only recent sessions)
    review_check = check_review_artifacts(branch=current_branch)

    # Warn only (agents still running) — no block
    if review_check.get('warn'):
        print(f"[pre_stop_check] {review_check['warn']}", file=sys.stderr)
        print(json.dumps({}))
        return

    # Review found issues → block
    if review_check.get('needs_review'):
        reason = f"[Pre-Stop Check] {review_check['reason']}."
        block_stop(session_id, reason)
        return

    # Recent review passed → skip code change check entirely
    if review_check.get('review_passed'):
        print(json.dumps({}))
        return

    # Layer 2: No recent review session — fall back to code change detection
    git_status = get_git_status()

    if not git_status['has_changes']:
        print(json.dumps({}))
        return

    all_changed = git_status['staged'] + git_status['unstaged']
    code_files = get_code_files(all_changed)

    if not code_files:
        print(json.dumps({}))
        return

    # Build block message with actionable review suggestions
    lines = [
        f"[Pre-Stop Check] {len(code_files)} code file(s) changed but not reviewed:",
    ]
    for f in code_files[:8]:
        lines.append(f"  - {f}")
    if len(code_files) > 8:
        lines.append(f"  ... and {len(code_files) - 8} more")

    # Layer 3: Detect security-sensitive files
    security_files = detect_security_files(code_files)
    if security_files:
        lines.append("")
        lines.append(f"[Security] {len(security_files)} security-sensitive file(s) detected:")
        for f in security_files[:5]:
            lines.append(f"  - {f}")
        lines.append("Action: Run code-reviewer agent (MANDATORY for security files).")

    # Check for incomplete work signals from last assistant message
    if check_incomplete_work(last_message):
        lines.append("")
        lines.append("[Incomplete Work] Last response contains unfinished work indicators.")

    lines.append("")
    if security_files:
        lines.append("Run code-reviewer agent for security review before stopping.")
    else:
        lines.append("Consider running /ultra-review or code-reviewer agent.")

    block_stop(session_id, "\n".join(lines))


if __name__ == '__main__':
    main()
