#!/usr/bin/env python3
"""
Agent Reminder Hook - PostToolUse
Enforces CLAUDE.md agent_system rules

Triggers agent suggestions based on:
- File types (.sol, .tsx, etc.)
- File paths (auth, payment, etc.)

This is a reminder only, does not block.
"""

import sys
import json
import re
import os

# File type to agent mapping
# NOTE: code-reviewer is NOT auto-triggered per file - only on explicit review request
FILE_TYPE_AGENTS = {
    '.sol': ['smart-contract-specialist', 'smart-contract-auditor'],
}

# Path patterns to agent mapping (case-insensitive)
PATH_AGENTS = [
    # Security-critical paths (MANDATORY)
    (r'/auth/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/login/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/password/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/payment/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/checkout/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/billing/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/crypto/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/encrypt/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/session/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),
    (r'/token/', ['pr-review-toolkit:code-reviewer'], 'MANDATORY'),

    # Admin/Permission paths
    (r'/admin/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/permission/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/role/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),
    (r'/acl/', ['pr-review-toolkit:code-reviewer'], 'Recommended'),

]

# Skills to suggest based on file type
FILE_SKILLS = {
    '.tsx': ['react-best-practices'],
    '.jsx': ['react-best-practices'],
    '.vue': ['web-design-guidelines'],
    '.svelte': ['web-design-guidelines'],
    '.css': ['web-design-guidelines'],
    '.scss': ['web-design-guidelines'],
}




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




def get_skills_for_file(file_path: str) -> list:
    """Get recommended skills based on file type."""
    recommendations = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext in FILE_SKILLS:
        skills = FILE_SKILLS[ext]
        recommendations.append({
            'skills': skills,
            'reason': f'File type: {ext}',
            'priority': 'Recommended'
        })

    return recommendations




def main():
    # Read stdin for hook input
    input_data = sys.stdin.read()
    try:
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(input_data)
        return

    tool_name = hook_input.get('tool_name')  # 官方文档：字段名是 tool_name
    tool_input = hook_input.get('tool_input', {})
    reminders = []

    skill_reminders = []

    # Check file-based agents for Edit/Write
    if tool_name in ('Edit', 'Write'):
        file_path = tool_input.get('file_path', '')
        recommendations = get_agents_for_file(file_path)

        for rec in recommendations:
            agents_str = ' + '.join(rec['agents'])
            reminders.append(f"[{rec['priority']}] {agents_str} - {rec['reason']}")

        # Check skills
        skill_recs = get_skills_for_file(file_path)
        for rec in skill_recs:
            skills_str = ' + '.join(rec['skills'])
            skill_reminders.append(f"[Skill] {skills_str} - {rec['reason']}")

    # Output reminders
    if reminders or skill_reminders:
        print("", file=sys.stderr)

        if reminders:
            print("[Agent Reminder] Consider invoking:", file=sys.stderr)
            for reminder in reminders:
                print(f"  {reminder}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Use Task tool with appropriate subagent_type to invoke agents.", file=sys.stderr)

        if skill_reminders:
            print("", file=sys.stderr)
            print("[Skill Reminder] Consider using:", file=sys.stderr)
            for reminder in skill_reminders:
                print(f"  {reminder}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Use Skill tool to invoke skills (e.g., /react-best-practices).", file=sys.stderr)
        print("", file=sys.stderr)

    # Always pass through (reminder only)
    print(input_data)


if __name__ == '__main__':
    main()
