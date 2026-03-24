#!/usr/bin/env python3
"""PostToolUse Hook - Lightweight observation capture.

Captures Write/Edit file changes and Bash test failures into observations table.
Skips Read/Grep/Glob (no signal). Max 20 observations per session.

Execution target: < 30ms (single DB check + optional insert).
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import memory_db

MAX_OBS_PER_SESSION = 20

# Patterns that indicate test execution
TEST_CMD_PATTERNS = re.compile(
    r"(npm\s+test|npx\s+(jest|vitest|mocha)|yarn\s+test|pnpm\s+test|"
    r"bun\s+test|jest\b|vitest\b|mocha\b|"
    r"pytest\b|python.*-m\s+(pytest|unittest)|"
    r"cargo\s+test|go\s+test|"
    r"dotnet\s+test|mix\s+test|flutter\s+test|"
    r"php\s+artisan\s+test|phpunit|"
    r"rspec|rake\s+test|ruby.*-e.*test|"
    r"make\s+test|gradle\s+test|mvn\s+test)", re.IGNORECASE
)

# Patterns that indicate test failure in output
TEST_FAIL_PATTERNS = re.compile(
    r"(FAIL[ED]*\b|FAILURES?\b|ERROR[S]?\b|error:|"
    r"AssertionError|AssertError|assert\w*Error|"
    r"tests?\s+failed|failing|failed\s+\d|"
    r"✗|✘|BROKEN|panic:|EXCEPTION)", re.IGNORECASE
)

# Significant non-test Bash commands worth recording
SIGNIFICANT_CMD_PATTERNS = re.compile(
    r"(git\s+(commit|push|merge|rebase|cherry-pick|tag)|"
    r"(npm|yarn|pnpm|bun|pip3?|cargo|go)\s+(run\s+build|build|install|add|publish)|"
    r"docker\s+(build|push|compose)|"
    r"make\b|gradle\s+build|mvn\s+(package|install|deploy)|"
    r"terraform\s+(apply|plan|destroy)|"
    r"kubectl\s+(apply|delete|rollout))", re.IGNORECASE
)

# Extract file paths from test command or output
FILE_PATH_PATTERN = re.compile(
    r'(?:^|\s|[/\\])(\S+\.(?:test|spec|_test|_spec)\.\w+)'  # test files
    r'|(?:FAIL|Error in|at )\s+(\S+\.\w{2,4})'               # failure references
    r'|(?:^|\s)((?:src|lib|app|tests?|spec)/\S+\.\w{2,4})',   # src paths
    re.MULTILINE
)


def main():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        pass

    if not raw or not raw.strip():
        print(json.dumps({}))
        return

    try:
        data = json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return

    if not isinstance(data, dict):
        print(json.dumps({}))
        return

    # Skip when running inside AI summarize daemon (prevents ghost sessions)
    if os.environ.get("ULTRA_AI_DAEMON") == "1":
        print(json.dumps({}))
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_output = data.get("tool_output", {})
    session_id = data.get("session_id", "")

    if not session_id or not tool_name:
        print(json.dumps({}))
        return

    # Only capture Write, Edit, Bash
    if tool_name not in ("Write", "Edit", "Bash"):
        print(json.dumps({}))
        return

    # Resolve internal session ID from content_session_id
    try:
        db_path = memory_db.get_db_path()
        conn = memory_db.init_db(db_path)

        # Find our session by content_session_id
        row = conn.execute(
            "SELECT id FROM sessions WHERE content_session_id = ? LIMIT 1",
            (session_id,)
        ).fetchone()

        if not row:
            # Create minimal session shell so observations are not lost.
            # Stop hook's upsert_session will merge via content_session_id.
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            internal_id = now.strftime("%Y%m%d-%H%M%S") + f"-{now.microsecond // 1000:03d}"
            conn.execute(
                "INSERT OR IGNORE INTO sessions "
                "(id, started_at, last_active, content_session_id) "
                "VALUES (?, ?, ?, ?)",
                (internal_id, now.isoformat(), now.isoformat(), session_id)
            )
            conn.commit()
        else:
            internal_id = row["id"]

        # Check observation count cap
        count = conn.execute(
            "SELECT COUNT(*) FROM observations WHERE session_id = ?",
            (internal_id,)
        ).fetchone()[0]

        if count >= MAX_OBS_PER_SESSION:
            conn.close()
            print(json.dumps({}))
            return

        # Process based on tool type
        if tool_name in ("Write", "Edit"):
            _capture_file_change(conn, internal_id, tool_name, tool_input)
        elif tool_name == "Bash":
            # Try test capture first, fall back to significant command capture
            command = ""
            if isinstance(tool_input, dict):
                command = tool_input.get("command", "")
            elif isinstance(tool_input, str):
                command = tool_input
            if command and TEST_CMD_PATTERNS.search(command):
                _capture_test_result(conn, internal_id, tool_input, tool_output)
            elif command:
                _capture_significant_command(conn, internal_id, command)

        conn.close()
    except Exception:
        print("[observation_capture] DB error", file=sys.stderr)

    print(json.dumps({}))


def _capture_file_change(conn, session_id: str, tool_name: str,
                         tool_input: dict) -> None:
    """Capture a Write/Edit observation."""
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    # Skip non-source files
    basename = os.path.basename(file_path)
    if basename.startswith(".") and not basename.endswith((".py", ".ts", ".js")):
        return

    # Shorten path for title
    short_path = file_path
    cwd = os.getcwd()
    if short_path.startswith(cwd):
        short_path = short_path[len(cwd):].lstrip("/")

    title = f"{tool_name}: {short_path}"
    if len(title) > 200:
        title = title[:197] + "..."

    memory_db.save_observation(
        conn, session_id,
        kind="edit",
        title=title,
        tool_name=tool_name,
        files=[short_path],
    )


def _capture_significant_command(conn, session_id: str, command: str) -> None:
    """Capture significant Bash commands (git, build, deploy) as lightweight observations."""
    if not SIGNIFICANT_CMD_PATTERNS.search(command):
        return

    # Reject package install guard (same as test capture)
    if re.search(r'\b(pip3?|pipx)\s+install\s+(pytest|unittest)', command, re.IGNORECASE):
        return

    # Short title from first meaningful part of command
    title = command.strip().split("\n")[0][:150]

    memory_db.save_observation(
        conn, session_id,
        kind="command",
        title=title,
        tool_name="Bash",
    )


def _extract_related_files(command: str, output: str) -> list:
    """Extract file paths from test command and output for cross-session matching."""
    files = set()
    for text in (command, output[:2000]):
        for match in FILE_PATH_PATTERN.finditer(text):
            for group in match.groups():
                if group:
                    # Clean up and keep just the filename or short path
                    path = group.strip().strip("'\"(),:")
                    if path and 2 < len(path) < 200:
                        files.add(path)
    return list(files)[:5]


def _capture_test_result(conn, session_id: str, tool_input,
                         tool_output) -> None:
    """Capture test failure observation from Bash output."""
    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")
    elif isinstance(tool_input, str):
        command = tool_input

    if not command or not TEST_CMD_PATTERNS.search(command):
        return

    # Reject package install commands (false positives for "pip install pytest" etc.)
    if re.search(r'\b(pip3?|pipx|npm|yarn|pnpm|bun)\s+install\b', command, re.IGNORECASE):
        return

    # Get output text — handle both string and dict formats
    output = ""
    if isinstance(tool_output, dict):
        output = tool_output.get("stdout", "") + tool_output.get("stderr", "")
        if not output:
            output = tool_output.get("output", "")
    elif isinstance(tool_output, str):
        output = tool_output

    if not output:
        return

    # Extract related file paths for cross-session matching
    related_files = _extract_related_files(command, output)

    # Check for failures
    if TEST_FAIL_PATTERNS.search(output):
        # Extract first failure line for title
        title = "Test failure"
        for line in output.split("\n"):
            line = line.strip()
            if TEST_FAIL_PATTERNS.search(line) and len(line) > 10:
                title = line[:200]
                break

        memory_db.save_observation(
            conn, session_id,
            kind="test_failure",
            title=title,
            detail=command[:500],
            tool_name="Bash",
            files=related_files,
        )
    else:
        # Test passed — also useful signal
        memory_db.save_observation(
            conn, session_id,
            kind="test_pass",
            title=f"Tests passed: {command[:100]}",
            tool_name="Bash",
            files=related_files,
        )


if __name__ == "__main__":
    main()
