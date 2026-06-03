#!/usr/bin/env python3
"""PreToolUse Hook - Mid-Workflow Goal Reminder + Grep advisory (v7.1).

Injects concise context via stderr at key decision points:
  Write|Edit: active task acceptance criteria (Goal-Always-Present substrate) —
              keeps the goal in view mid-session to prevent drift.
  Grep:       symbol-query advisory pointing at code-review-graph MCP if the
              pattern looks like a symbol lookup. Sensor only — never blocks.

Memory归位 (2026-06-02): cross-session memory recall (past test failures, edit
history, learned lessons from memory.db) was removed — memory.db is gone and
claude-mem now owns cross-session recall (query it on demand). This hook now
injects ONLY the live active-task acceptance criteria, never historical memory.

Fires on: Write|Edit|Grep
Performance: <50ms common case
Rate-limited: once per file per session, max 10 injections per session
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_INJECTIONS = 10
GIT_TIMEOUT = 3

SOURCE_EXTENSIONS = {
    '.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java',
    '.sol', '.rb', '.vue', '.svelte', '.sh',
}


def get_tracker_path(session_id: str) -> str:
    return os.path.join(tempfile.gettempdir(), f".claude_recall_{session_id}")


def load_recalled(session_id: str) -> set:
    try:
        with open(get_tracker_path(session_id)) as f:
            return set(line.strip() for line in f if line.strip())
    except (OSError, FileNotFoundError):
        return set()


def mark_recalled(session_id: str, file_path: str) -> None:
    tracker = get_tracker_path(session_id)
    try:
        with open(tracker, 'a') as f:
            f.write(file_path + '\n')
        os.chmod(tracker, 0o600)
    except OSError:
        pass


_SYMBOL_PATTERN = re.compile(
    r'(^|\b)(def|class|function|fn|func|interface|type|struct|impl)\s+\w+'
)
# Require mixed case to avoid matching all-caps tokens like 'TODO', 'API', 'URL'
_CAMEL_OR_PASCAL = re.compile(
    r'^([A-Z][a-z]+(?:[A-Z0-9]\w*)*|[a-z]+(?:[A-Z]\w+)+)$'
)


def _looks_like_symbol_query(pattern: str) -> bool:
    """Heuristic: does this Grep pattern look like a symbol lookup?

    Examples that match: 'class UserRepo', 'function authenticate', 'PaymentService',
    'getUserById'. Examples that don't: 'TODO', 'error.*timeout', 'foo bar'.
    """
    p = pattern.strip()
    if not p or len(p) > 80 or any(c in p for c in ' \t|()[]\\'):
        # multi-token / regex-heavy → fuzzy text, not symbol
        return bool(_SYMBOL_PATTERN.search(p)) and len(p) < 80
    return bool(_SYMBOL_PATTERN.search(p) or _CAMEL_OR_PASCAL.match(p))


def handle_grep_advisory(tool_input: dict, session_id: str) -> None:
    """v7: Grep symbol-query advisory. Sensor only — never blocks."""
    pattern = tool_input.get("pattern", "")
    if not pattern or not _looks_like_symbol_query(pattern):
        return

    if session_id:
        recalled = load_recalled(session_id)
        token = f"grep:{pattern[:50]}"
        if token in recalled or len(recalled) >= MAX_INJECTIONS:
            return
        mark_recalled(session_id, token)

    print(
        f"[Grep advisory] '{pattern[:60]}' looks like a symbol query.\n"
        f"  If project has code-review-graph MCP, prefer:\n"
        f"    query_graph(pattern='symbol_search', query='{pattern[:60]}')\n"
        f"  → callers/callees/imports without file scanning. Grep fallback OK if no graph.",
        file=sys.stderr,
    )


def _get_active_task_acceptance() -> list:
    """v7 Goal-Always-Present: read in_progress task's acceptance criteria.

    Returns up to ~3 lines for stderr injection. Empty list if no .ultra/ or no
    in_progress task.
    """
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        root = Path(proc.stdout.strip())
        tasks_path = root / '.ultra' / 'tasks' / 'tasks.json'
        if not tasks_path.exists():
            return []

        tasks_data = json.loads(tasks_path.read_text(encoding='utf-8'))
        in_progress = [
            t for t in tasks_data.get('tasks', [])
            if t.get('status') == 'in_progress'
        ]
        if not in_progress:
            return []
        t = in_progress[0]
        tid = t.get('id', '?')
        title = t.get('title', '?')
        out = [f"  Active task {tid}: {title[:80]}"]

        ctx_file = root / '.ultra' / 'tasks' / 'contexts' / f"task-{tid}.md"
        if ctx_file.exists():
            content = ctx_file.read_text(encoding='utf-8')
            if '## Acceptance Criteria' in content:
                section = content.split('## Acceptance Criteria', 1)[1]
                section = section.split('\n---\n', 1)[0]
                # Take first 2 non-comment, non-placeholder bullet lines
                bullets = []
                in_comment = False
                for line in section.split('\n'):
                    s = line.strip()
                    if not s:
                        continue
                    if '<!--' in s and '-->' not in s:
                        in_comment = True
                        continue
                    if in_comment:
                        if '-->' in s:
                            in_comment = False
                        continue
                    if s.startswith('<!--') and s.endswith('-->'):
                        continue
                    if s.startswith('_(') and s.endswith(')_'):
                        continue
                    if s.startswith('- ') and len(s) > 4:
                        bullets.append(s[:120])
                        if len(bullets) >= 2:
                            break
                for b in bullets:
                    out.append(f"    {b}")
        return out
    except Exception:
        return []


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({}))
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "")

    # v7: Grep advisory branch (symbol-query routing hint)
    if tool_name == "Grep":
        handle_grep_advisory(tool_input, session_id)
        print(json.dumps({}))
        return

    if tool_name not in ("Write", "Edit"):
        print(json.dumps({}))
        return

    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({}))
        return

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SOURCE_EXTENSIONS:
        print(json.dumps({}))
        return

    # Rate limit: skip if already injected or quota exhausted
    if session_id:
        recalled = load_recalled(session_id)
        if file_path in recalled or len(recalled) >= MAX_INJECTIONS:
            print(json.dumps({}))
            return

    # v7 Goal-Always-Present: inject active task acceptance criteria
    ac_lines = _get_active_task_acceptance()
    if not ac_lines:
        print(json.dumps({}))
        return

    lines = [f"[Goal reminder — editing {filename}]"]
    lines.extend(ac_lines)
    print("\n".join(lines), file=sys.stderr)

    if session_id:
        mark_recalled(session_id, file_path)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
