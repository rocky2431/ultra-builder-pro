#!/usr/bin/env python3
"""
Session Context Hook - SessionStart (v7.0 — Goal-Always-Present substrate)

Loads development context at session start.

Provides:
- Current git branch and recent commits
- Modified files status
- Last session one-liner from memory DB (~50 tokens)
- Recent cross-branch learnings (Hindsight-inspired)
- v7: tools status (rtk / .ultra availability) — quick situational awareness
- v7: north-star (project goal + active task acceptance criteria) — Goal-Always-Present
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path


def run_cmd(cmd: list, cwd: str = '') -> str:
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            timeout=3
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"[session_context] Command failed: {' '.join(cmd)}: {e}", file=sys.stderr)
    return ''


def get_git_context() -> list:
    """Get git repository context."""
    context = []

    # Check if in git repo
    if not run_cmd(['git', 'rev-parse', '--is-inside-work-tree']):
        return context

    # Current branch
    branch = run_cmd(['git', 'branch', '--show-current'])
    if branch:
        context.append(f"Branch: {branch}")

    # Recent commits (last 3)
    log = run_cmd(['git', 'log', '--oneline', '-3'])
    if log:
        context.append("Recent commits:")
        for line in log.split('\n'):
            context.append(f"  {line}")

    # Modified files
    status = run_cmd(['git', 'status', '--short'])
    if status:
        lines = status.split('\n')
        context.append(f"Modified files: {len(lines)}")
        for line in lines[:5]:
            context.append(f"  {line}")
        if len(lines) > 5:
            context.append(f"  ... and {len(lines) - 5} more")

    return context


def get_project_context() -> list:
    """Get project-specific context."""
    context = []

    # Check for package.json
    if os.path.exists('package.json'):
        try:
            with open('package.json', 'r') as f:
                pkg = json.load(f)
                name = pkg.get('name', 'unknown')
                context.append(f"Project: {name} (Node.js)")
        except Exception:
            pass

    # Check for pyproject.toml
    elif os.path.exists('pyproject.toml'):
        context.append("Project: Python (pyproject.toml)")

    # Check for Cargo.toml
    elif os.path.exists('Cargo.toml'):
        context.append("Project: Rust (Cargo.toml)")

    # Check for go.mod
    elif os.path.exists('go.mod'):
        context.append("Project: Go (go.mod)")

    return context


def get_last_session_oneliner() -> str:
    """Get a one-liner about the last session from memory DB.

    Direct import instead of subprocess for ~100ms faster startup.
    Returns empty string if DB doesn't exist or has no records.
    Adds ~50 tokens to context. Fails silently.
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import memory_db
        db_path = memory_db.get_db_path()
        if not db_path.exists():
            return ""
        conn = memory_db.init_db(db_path)
        result = memory_db.get_latest(conn)
        conn.close()
        if result:
            return memory_db.format_oneliner(result)
    except Exception:
        pass
    return ""


def get_branch_memory(branch: str) -> list:
    """Query memory DB for recent sessions with summaries on this branch.

    Prefers structured summaries (session_summaries.completed) over legacy.
    Returns up to 3 session summaries for context continuity.
    Adds ~150 tokens. Fails silently.
    """
    if not branch:
        return []

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import memory_db

        db_path = memory_db.get_db_path()
        if not db_path.exists():
            return []

        conn = memory_db.init_db(db_path)
        rows = conn.execute(
            """SELECT s.id, s.last_active, s.summary,
                      ss.completed as ss_completed, ss.request as ss_request
               FROM sessions s
               LEFT JOIN session_summaries ss ON s.id = ss.session_id
               WHERE s.branch = ? AND (s.summary != '' OR ss.status = 'ready')
               ORDER BY s.last_active DESC LIMIT 3""",
            (branch,)
        ).fetchall()
        conn.close()

        lines = []
        for row in rows:
            date = row["last_active"][:10]

            # Prefer structured summary
            if row["ss_completed"]:
                short = row["ss_completed"]
            elif row["summary"]:
                summary = row["summary"]
                short = summary.split("\n")[0].strip()
                if short.startswith("- "):
                    short = short[2:]
                if short.startswith("## "):
                    for s_line in summary.split("\n"):
                        s_line = s_line.strip()
                        if s_line.startswith("- ") and len(s_line) > 5:
                            short = s_line[2:]
                            break
            else:
                continue

            if len(short) > 120:
                short = short[:117] + "..."
            lines.append(f"  - [{date}] {short}")

        return lines
    except Exception:
        pass
    return []


def get_semantic_context(source: str, branch: str = "") -> list:
    """Use Chroma semantic search to find related sessions.

    Only activates for startup sessions (not compact) and when there are
    enough sessions (5+) to make semantic search worthwhile.
    Adds ~100 tokens. Fails silently.
    """
    if source != "startup":
        return []

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import memory_db

        db_path = memory_db.get_db_path()
        if not db_path.exists():
            return []

        conn = memory_db.init_db(db_path)
        total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        if total < 5:
            conn.close()
            return []

        # Build richer query: branch + last commit (MemPalace L1 inspired)
        query_parts = []
        if branch:
            query_parts.append(branch)
        last_commit = run_cmd(["git", "log", "--oneline", "-1", "--format=%s"])
        if last_commit:
            query_parts.append(last_commit)
        if not query_parts:
            query_parts.append(Path.cwd().name)
        query = " ".join(query_parts)
        results = memory_db.semantic_search(query, limit=3, conn=conn)
        conn.close()

        if not results:
            return []

        lines = ["Semantically related sessions:"]
        for s in results:
            date = s.get("last_active", "")[:10]
            summary = s.get("summary", "")
            if summary:
                short = summary.split("\n")[0].strip()
                if len(short) > 100:
                    short = short[:97] + "..."
                lines.append(f"  - [{date}] {short}")
        return lines if len(lines) > 1 else []
    except Exception:
        return []


def get_recent_learnings() -> list:
    """Get recent non-trivial learned insights across all branches.

    Surfaces Haiku-extracted 'learned' field from session_summaries.
    Inspired by Hindsight's consolidation: make past learnings visible.
    Adds ~100 tokens. Fails silently.
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import memory_db

        db_path = memory_db.get_db_path()
        if not db_path.exists():
            return []

        conn = memory_db.init_db(db_path)
        rows = conn.execute(
            """SELECT ss.learned, s.branch, s.last_active
               FROM session_summaries ss
               JOIN sessions s ON ss.session_id = s.id
               WHERE ss.learned != '' AND ss.status = 'ready'
               ORDER BY s.last_active DESC LIMIT 5""",
        ).fetchall()
        conn.close()

        if not rows:
            return []

        lines = ["Recent learnings:"]
        seen = set()
        for row in rows:
            learned = row["learned"].strip()
            if learned and learned not in seen:
                seen.add(learned)
                date = row["last_active"][:10]
                branch_name = row["branch"] or "?"
                short = learned.replace("|", ",")
                if len(short) > 120:
                    short = short[:117] + "..."
                lines.append(f"  - [{date}, {branch_name}] {short}")

        return lines if len(lines) > 1 else []
    except Exception:
        return []


def _extract_md_section(content: str, header: str, max_chars: int = 300) -> str:
    """Extract first non-placeholder content from a markdown section header to next `---`.

    Properly handles multi-line HTML comments, blockquotes, and placeholder markers.
    """
    if header not in content:
        return ""
    section = content.split(header, 1)[1].split('\n---\n', 1)[0]
    out = []
    in_comment = False
    for line in section.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        # Track multi-line HTML comments (line may contain both open and close)
        if '<!--' in stripped and '-->' not in stripped:
            in_comment = True
            continue
        if in_comment:
            if '-->' in stripped:
                in_comment = False
            continue
        # Single-line comment
        if stripped.startswith('<!--') and stripped.endswith('-->'):
            continue
        if stripped.startswith('>'):
            stripped = stripped[1:].strip()
        if not stripped:
            continue
        # Skip placeholder markers like _(not yet defined)_ or _(criterion 1)_
        if stripped.startswith('_(') and stripped.endswith(')_'):
            continue
        # Skip checklist markers without content
        if stripped in ('- [ ]', '- [x]'):
            continue
        out.append(stripped)
        if sum(len(s) for s in out) > max_chars:
            break
    result = ' '.join(out)
    return result[:max_chars].strip()


def get_tools_status() -> list:
    """v7: report harness tool availability. Minimal — keep token cost low."""
    lines = []
    try:
        rtk_ok = subprocess.run(
            ['which', 'rtk'], capture_output=True, text=True, timeout=1
        ).returncode == 0
        lines.append(f"  rtk: {'✓ active (auto Bash rewrite)' if rtk_ok else '✗ not installed'}")
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=1
        )
        if proc.returncode == 0 and proc.stdout.strip():
            ultra = Path(proc.stdout.strip()) / '.ultra'
            if ultra.exists():
                phil = ultra / 'PHILOSOPHY.md'
                ns = ultra / 'north-star.md'
                lines.append(
                    f"  .ultra: ✓ {'philosophy' if phil.exists() else 'no-philosophy'} | "
                    f"{'north-star' if ns.exists() else 'no-north-star'}"
                )
    except Exception:
        pass

    return ["[Tools]"] + lines if lines else []


def get_north_star_context() -> list:
    """v7 Goal-Always-Present: inject project + active task north-star at SessionStart."""
    lines = []
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=1
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        root = Path(proc.stdout.strip())
        ns_path = root / '.ultra' / 'north-star.md'
        if not ns_path.exists():
            return []

        content = ns_path.read_text(encoding='utf-8')
        one_line = _extract_md_section(content, '## One-line', max_chars=250)
        hard = _extract_md_section(content, '## Hard Constraints', max_chars=400)

        if one_line:
            lines.append(f"  Goal: {one_line}")
        if hard:
            lines.append(f"  Hard constraints: {hard}")

        # Active task acceptance criteria
        tasks_path = root / '.ultra' / 'tasks' / 'tasks.json'
        if tasks_path.exists():
            try:
                tasks_data = json.loads(tasks_path.read_text(encoding='utf-8'))
                in_progress = [
                    t for t in tasks_data.get('tasks', [])
                    if t.get('status') == 'in_progress'
                ]
                if in_progress:
                    t = in_progress[0]
                    tid = t.get('id', '?')
                    title = t.get('title', '?')
                    lines.append(f"  Active task {tid}: {title}")
                    ctx_file = root / '.ultra' / 'tasks' / 'contexts' / f"task-{tid}.md"
                    if ctx_file.exists():
                        ctx_md = ctx_file.read_text(encoding='utf-8')
                        ac = _extract_md_section(ctx_md, '## Acceptance Criteria', max_chars=300)
                        if ac:
                            lines.append(f"  Acceptance: {ac}")
            except Exception:
                pass
    except Exception:
        pass

    return ["[North Star]"] + lines if lines else []


def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[session_context] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    if not isinstance(hook_input, dict):
        print(json.dumps({}))
        return

    source = hook_input.get('source', 'startup')

    # Build context
    context_lines = [
        f"[Session Context] {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Session type: {source}",
        ""
    ]

    # Add git context
    git_ctx = get_git_context()
    if git_ctx:
        context_lines.extend(git_ctx)
        context_lines.append("")

    # Add project context
    proj_ctx = get_project_context()
    if proj_ctx:
        context_lines.extend(proj_ctx)

    # Add last session one-liner from memory DB
    last_session = get_last_session_oneliner()
    if last_session:
        context_lines.append("")
        context_lines.append(last_session)

    # Add branch-relevant memory (recent sessions on same branch)
    branch = ''
    for line in git_ctx:
        if line.startswith("Branch:"):
            branch = line.replace("Branch:", "").strip()
            break

    branch_mem = get_branch_memory(branch)
    if branch_mem:
        context_lines.append("")
        context_lines.append("Related sessions on this branch:")
        context_lines.extend(branch_mem)

    # Semantic recall (opt-in: only when enough sessions exist)
    semantic_lines = get_semantic_context(source, branch)
    if semantic_lines:
        context_lines.append("")
        context_lines.extend(semantic_lines)

    # Recent learnings (Hindsight-inspired: surface past insights)
    learnings_lines = get_recent_learnings()
    if learnings_lines:
        context_lines.append("")
        context_lines.extend(learnings_lines)

    # v7: tools status (rtk / .ultra availability)
    tools_lines = get_tools_status()
    if tools_lines:
        context_lines.append("")
        context_lines.extend(tools_lines)

    # v7: north-star (Goal-Always-Present substrate — every session sees the goal)
    ns_lines = get_north_star_context()
    if ns_lines:
        context_lines.append("")
        context_lines.extend(ns_lines)

    # Output context for AI
    result = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(context_lines)
        }
    }
    print(json.dumps(result))


if __name__ == '__main__':
    main()
