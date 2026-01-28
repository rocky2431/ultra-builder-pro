#!/usr/bin/env python3
"""
Task Persistence Hook - PostToolUse
Enforces CLAUDE.md workflow_tracking rule:
"update both session and persistent"

When TaskUpdate is called, remind to sync to .ultra/tasks/
"""

import sys
import json
import os


def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    tool_name = hook_input.get('tool_name')

    # Only check TaskUpdate and TaskCreate
    if tool_name not in ('TaskUpdate', 'TaskCreate'):
        print(json.dumps({}))
        return

    # Check if .ultra/tasks/ exists in current working directory
    cwd = os.getcwd()
    ultra_tasks_dir = os.path.join(cwd, '.ultra', 'tasks')

    reminder_lines = []

    if tool_name == 'TaskUpdate':
        tool_input = hook_input.get('tool_input', {})
        task_id = tool_input.get('taskId', '')
        status = tool_input.get('status', '')

        if status == 'completed':
            reminder_lines = [
                "[TASK PERSISTENCE] Task marked completed",
                "",
                "CLAUDE.md workflow_tracking rule: 'update both session and persistent'",
                "",
                f"If .ultra/tasks/ exists, sync task {task_id} status to persistent storage.",
                f"Path: {ultra_tasks_dir}/",
            ]

    elif tool_name == 'TaskCreate':
        tool_input = hook_input.get('tool_input', {})
        subject = tool_input.get('subject', '')

        if os.path.isdir(ultra_tasks_dir):
            reminder_lines = [
                "[TASK PERSISTENCE] New task created",
                "",
                "CLAUDE.md workflow_tracking rule: 'update both session and persistent'",
                "",
                f"Consider persisting task '{subject[:50]}' to .ultra/tasks/",
                f"Path: {ultra_tasks_dir}/",
            ]

    if reminder_lines:
        reminder_message = "\n".join(reminder_lines)
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": reminder_message
            }
        }
        print(json.dumps(result))
    else:
        print(json.dumps({}))


if __name__ == '__main__':
    main()
