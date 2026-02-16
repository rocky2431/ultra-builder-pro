#!/usr/bin/env python3
"""
Pre-Stop Check Hook - Stop
Checks for unreviewed code changes before session ends.

Three-layer check:
1. Review artifacts: If a recent (<2h) ultra-review session exists:
   - P0 unresolved → block once, allow on second attempt (marker-based)
   - APPROVE/COMMENT → allow stop (review passed)
   - Incomplete + < 15min old → warn only (agents may still be running)
   - Incomplete + >= 15min old → block once, allow on second attempt (abandoned)
2. Code changes (fallback): If no recent review session:
   - First trigger: block + create marker → remind to run review
   - Second trigger: marker exists → allow stop

Marker file: /tmp/.claude_review_done_<git_hash> (code changes)
             /tmp/.claude_review_session_<session_name> (review sessions)
Old marker files (>24h) are cleaned up automatically.
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


MARKER_PREFIX = ".claude_review_done_"
SESSION_MARKER_PREFIX = ".claude_review_session_"
GIT_TIMEOUT = 10  # seconds
MARKER_MAX_AGE = 86400  # 24 hours
INCOMPLETE_GRACE_PERIOD = 900  # 15 min - agents may still be running


def cleanup_old_markers() -> None:
    """Remove marker files older than MARKER_MAX_AGE seconds."""
    try:
        tmp_dir = tempfile.gettempdir()
        now = time.time()
        for prefix in (MARKER_PREFIX, SESSION_MARKER_PREFIX):
            pattern = os.path.join(tmp_dir, f"{prefix}*")
            for path in glob_module.glob(pattern):
                try:
                    if now - os.path.getmtime(path) > MARKER_MAX_AGE:
                        os.unlink(path)
                except OSError:
                    pass
    except Exception:
        pass


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
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=GIT_TIMEOUT
        )
        if proc.returncode != 0:
            print("[pre_stop_check] Not in a git repo, skipping", file=sys.stderr)
            return result

        proc = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=GIT_TIMEOUT
        )

        if proc.returncode != 0:
            print(f"[pre_stop_check] git status failed: {proc.stderr.strip()}", file=sys.stderr)
            return result

        for line in proc.stdout.strip().split('\n'):
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
    excluded_extensions = {'.md', '.txt', '.log'}
    return [f for f in files
            if os.path.splitext(f)[1].lower() in code_extensions
            and os.path.splitext(f)[1].lower() not in excluded_extensions]


def get_changes_hash(files: list) -> str:
    """Generate a hash based on the set of changed files."""
    content = "\n".join(sorted(files))
    return hashlib.md5(content.encode()).hexdigest()[:12]


def get_marker_path(changes_hash: str) -> str:
    """Get the marker file path for a given changes hash."""
    return os.path.join(tempfile.gettempdir(), f"{MARKER_PREFIX}{changes_hash}")


def is_review_done(changes_hash: str) -> bool:
    """Check if review has been completed for this set of changes."""
    return os.path.exists(get_marker_path(changes_hash))


def mark_review_blocked(changes_hash: str) -> bool:
    """Mark that we've blocked once for this set of changes.

    On the first block, create a marker file. On the next stop attempt,
    the hook will see the marker and allow stop (review was presumably done).
    Returns True if marker was created successfully.
    """
    marker_path = get_marker_path(changes_hash)
    try:
        with open(marker_path, 'w') as f:
            f.write("blocked_once")
        return True
    except OSError as e:
        print(f"[pre_stop_check] Failed to create marker file: {e}", file=sys.stderr)
        return False


SESSION_MAX_AGE = 7200  # 2 hours - only consider recent review sessions


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


def check_review_artifacts() -> dict:
    """Check if a recent ultra-review session for the current branch has unresolved P0s.

    Uses index.json (branch-scoped) with fallback to directory scan (time-scoped).
    Avoids false positives from old or unrelated review sessions.

    Returns:
        dict with 'needs_review' (bool), optionally 'reason' (str),
        and 'review_passed' (bool) if a recent passing review exists.
    """
    maybe_reviews_dir = get_project_reviews_dir()
    if maybe_reviews_dir is None or not maybe_reviews_dir.exists():
        return {'needs_review': False, 'review_passed': False}
    reviews_dir: Path = maybe_reviews_dir

    current_branch = get_current_branch()

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
                        'session_id': session_id,
                        'reason': f"Review found {p0_count} P0 critical issue(s) - fix before stopping"
                    }

                if verdict == 'REQUEST_CHANGES':
                    # P1-only REQUEST_CHANGES: block once with marker
                    return {
                        'needs_review': True,
                        'review_passed': False,
                        'session_id': session_id,
                        'reason': f"Review verdict is REQUEST_CHANGES (P1 issues unresolved)"
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
            # Abandoned: use marker-based block
            return {
                'needs_review': True,
                'review_passed': False,
                'session_id': latest.name,
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
            'session_id': latest.name,
            'reason': f"Review found {p0_count} P0 critical issue(s) - fix before stopping"
        }

    if verdict == 'REQUEST_CHANGES':
        # P1-only REQUEST_CHANGES: block once with marker
        return {
            'needs_review': True,
            'review_passed': False,
            'session_id': latest.name,
            'reason': f"Review verdict is REQUEST_CHANGES (P1 issues unresolved)"
        }

    return {'needs_review': False, 'review_passed': True}


def main():
    try:
        input_data = sys.stdin.read()
        json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[pre_stop_check] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    cleanup_old_markers()

    # Check review artifacts first (only recent sessions)
    review_check = check_review_artifacts()

    # Warn only (agents still running) — no block, early return
    if review_check.get('warn'):
        print(f"[pre_stop_check] {review_check['warn']}", file=sys.stderr)
        print(json.dumps({}))
        return

    # Block with escape hatch: marker-based (block once, allow on second attempt)
    if review_check.get('needs_review'):
        session_id = review_check.get('session_id', 'unknown')
        marker_path = os.path.join(
            tempfile.gettempdir(),
            f"{SESSION_MARKER_PREFIX}{session_id}"
        )

        if os.path.exists(marker_path):
            # Second attempt — allow stop, warn user
            reason = review_check['reason']
            print(f"[pre_stop_check] Allowing stop (second attempt). Unresolved: {reason}", file=sys.stderr)
            print(json.dumps({}))
            return

        # First attempt — block and create marker
        try:
            with open(marker_path, 'w') as f:
                f.write(f"blocked_at={time.time()}")
        except OSError:
            pass

        result = {
            "decision": "block",
            "reason": f"[Pre-Stop Check] {review_check['reason']}. Stopping anyway on next attempt."
        }
        print(json.dumps(result))
        return

    # Recent review passed → skip code change check entirely
    if review_check.get('review_passed'):
        print(json.dumps({}))
        return

    # No recent review session — fall back to code change detection
    # Skip for main/master: merged code was already reviewed on its feature branch
    current_branch = get_current_branch()
    if current_branch in ('main', 'master'):
        print(json.dumps({}))
        return

    git_status = get_git_status()

    if not git_status['has_changes']:
        print(json.dumps({}))
        return

    all_changed = git_status['staged'] + git_status['unstaged']
    code_files = get_code_files(all_changed)

    if not code_files:
        print(json.dumps({}))
        return

    changes_hash = get_changes_hash(all_changed)

    # Already blocked once for this set of changes → allow stop
    if is_review_done(changes_hash):
        print(json.dumps({}))
        return

    # First time: block and create marker
    mark_review_blocked(changes_hash)

    lines = [
        f"[Pre-Stop Check] {len(code_files)} code file(s) changed:",
    ]
    for f in code_files[:8]:
        lines.append(f"  - {f}")
    if len(code_files) > 8:
        lines.append(f"  ... and {len(code_files) - 8} more")

    lines.append("")
    lines.append("Unreviewed code changes detected. Stopping anyway on next attempt.")

    result = {
        "decision": "block",
        "reason": "\n".join(lines)
    }
    print(json.dumps(result))


if __name__ == '__main__':
    main()
