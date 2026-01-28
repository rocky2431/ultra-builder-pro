#!/usr/bin/env python3
"""
Agent Reminder Hook - PostToolUse
Enforces CLAUDE.md agent_system rules (lines 238-245)

Triggers agent suggestions based on:
- File types (.sol, .tsx, etc.)
- File paths (auth, payment, etc.)
- Build command failures

This is a reminder only, does not block.
"""

import sys
import json
import re
import os

# File type to agent mapping
FILE_TYPE_AGENTS = {
    '.sol': ['smart-contract-specialist', 'smart-contract-auditor'],
    '.tsx': ['frontend-developer', 'pr-review-toolkit:code-reviewer'],
    '.jsx': ['frontend-developer', 'pr-review-toolkit:code-reviewer'],
    '.css': ['frontend-developer'],
    '.scss': ['frontend-developer'],
    '.less': ['frontend-developer'],
    '.vue': ['frontend-developer', 'pr-review-toolkit:code-reviewer'],
    '.svelte': ['frontend-developer', 'pr-review-toolkit:code-reviewer'],
    '.md': ['doc-updater'],
    '.rst': ['doc-updater'],
}

# Path patterns to agent mapping (case-insensitive)
PATH_AGENTS = [
    # Security-critical paths (MANDATORY)
    (r'/auth/', ['security-reviewer'], 'MANDATORY'),
    (r'/login/', ['security-reviewer'], 'MANDATORY'),
    (r'/password/', ['security-reviewer'], 'MANDATORY'),
    (r'/payment/', ['security-reviewer'], 'MANDATORY'),
    (r'/checkout/', ['security-reviewer'], 'MANDATORY'),
    (r'/billing/', ['security-reviewer'], 'MANDATORY'),
    (r'/crypto/', ['security-reviewer'], 'MANDATORY'),
    (r'/encrypt/', ['security-reviewer'], 'MANDATORY'),
    (r'/session/', ['security-reviewer'], 'MANDATORY'),
    (r'/token/', ['security-reviewer'], 'MANDATORY'),

    # Admin/Permission paths
    (r'/admin/', ['security-reviewer'], 'Recommended'),
    (r'/permission/', ['security-reviewer'], 'Recommended'),
    (r'/role/', ['security-reviewer'], 'Recommended'),
    (r'/acl/', ['security-reviewer'], 'Recommended'),

    # API paths
    (r'/api/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/middleware/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/handler/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/controller/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/route/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),

    # Test paths
    (r'/__tests__/', ['tdd-guide'], 'Recommended'),
    (r'/test/', ['tdd-guide'], 'Recommended'),
    (r'\.test\.', ['tdd-guide'], 'Recommended'),
    (r'\.spec\.', ['tdd-guide'], 'Recommended'),
    (r'/e2e/', ['e2e-runner'], 'Recommended'),

    # Documentation paths
    (r'/docs/', ['doc-updater'], 'Recommended'),
    (r'readme', ['doc-updater'], 'Recommended'),
    (r'changelog', ['doc-updater'], 'Recommended'),

    # Infrastructure paths (need planning)
    (r'/infrastructure/', ['planner', 'architect'], 'Recommended'),
    (r'/terraform/', ['planner'], 'Recommended'),
    (r'/docker/', ['planner'], 'Recommended'),
    (r'/k8s/', ['planner'], 'Recommended'),
    (r'/kubernetes/', ['planner'], 'Recommended'),
]

# Build commands that trigger build-error-resolver on failure
BUILD_COMMANDS = [
    r'\bnpm\s+run\s+build\b',
    r'\byarn\s+build\b',
    r'\bpnpm\s+(?:run\s+)?build\b',
    r'\bcargo\s+build\b',
    r'\bgo\s+build\b',
    r'\bmake\b',
    r'\btsc\b',
    r'\bnext\s+build\b',
    r'\bvite\s+build\b',
    r'\bgradle\s+build\b',
    r'\bmvn\s+(?:compile|package|install)\b',
]

# Test commands that trigger tdd-guide on failure
TEST_COMMANDS = [
    r'\bnpm\s+(?:run\s+)?test\b',
    r'\byarn\s+test\b',
    r'\bpnpm\s+(?:run\s+)?test\b',
    r'\bjest\b',
    r'\bvitest\b',
    r'\bpytest\b',
    r'\bcargo\s+test\b',
    r'\bgo\s+test\b',
]


def get_agents_for_file(file_path: str) -> list:
    """Get recommended agents based on file type and path."""
    recommendations = []

    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext in FILE_TYPE_AGENTS:
        agents = FILE_TYPE_AGENTS[ext]
        priority = 'MANDATORY' if ext == '.sol' else 'Recommended'
        recommendations.append({
            'agents': agents,
            'reason': f'File type: {ext}',
            'priority': priority
        })

    # Check path patterns
    path_lower = file_path.lower()
    for pattern, agents, priority in PATH_AGENTS:
        if re.search(pattern, path_lower):
            recommendations.append({
                'agents': agents,
                'reason': f'Path matches: {pattern}',
                'priority': priority
            })

    return recommendations


def check_command_failure(tool_name: str, tool_input: dict, tool_result: dict) -> list:
    """Check if a Bash command failed and return appropriate agents."""
    if tool_name != 'Bash':
        return []

    command = tool_input.get('command', '')
    exit_code = tool_result.get('exit_code', 0)

    if exit_code == 0:
        return []

    agents = []

    # Check build commands
    for pattern in BUILD_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            agents.append(('build-error-resolver', 'Build command failed'))
            break

    # Check test commands
    for pattern in TEST_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            agents.append(('tdd-guide', 'Test command failed - follow TDD workflow'))
            break

    return agents


def main():
    # Read stdin for hook input
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(input_data)
        return

    tool_name = hook_input.get('tool')
    tool_input = hook_input.get('tool_input', {})
    tool_result = hook_input.get('tool_result', {})

    reminders = []

    # Check file-based agents for Edit/Write
    if tool_name in ('Edit', 'Write'):
        file_path = tool_input.get('file_path', '')
        recommendations = get_agents_for_file(file_path)

        for rec in recommendations:
            agents_str = ' + '.join(rec['agents'])
            reminders.append(f"[{rec['priority']}] {agents_str} - {rec['reason']}")

    # Check for command failures (build/test)
    failed_agents = check_command_failure(tool_name, tool_input, tool_result)
    for agent, reason in failed_agents:
        reminders.append(f"[Recommended] {agent} - {reason}")

    # Output reminders
    if reminders:
        print("", file=sys.stderr)
        print("[Agent Reminder] Consider invoking:", file=sys.stderr)
        for reminder in reminders:
            print(f"  {reminder}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Use Task tool with appropriate subagent_type to invoke agents.", file=sys.stderr)
        print("", file=sys.stderr)

    # Always pass through (reminder only)
    print(input_data)


if __name__ == '__main__':
    main()
