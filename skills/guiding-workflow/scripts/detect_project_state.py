#!/usr/bin/env python3
"""
Project State Detection Script

Analyzes project filesystem to determine current development phase
and suggest next workflow steps.

Usage:
    python detect_project_state.py [project-path]
    python detect_project_state.py  # Uses current directory
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class ProjectState:
    """Represents the current state of a project."""
    has_ultra_dir: bool = False
    has_specs: bool = False
    has_tasks: bool = False
    has_research: bool = False
    has_uncommitted_changes: bool = False
    has_tests: bool = False

    specs_complete: bool = False
    tasks_completed: int = 0
    tasks_total: int = 0
    test_files_count: int = 0

    current_phase: str = "unknown"
    suggested_command: str = ""
    suggestion_reason: str = ""

    warnings: List[str] = field(default_factory=list)
    completed_items: List[str] = field(default_factory=list)
    pending_items: List[str] = field(default_factory=list)

    session_recovery: Optional[Dict] = None


class ProjectStateDetector:
    """Detects project state from filesystem signals."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()

    def detect(self) -> ProjectState:
        """Analyze project and return current state."""
        state = ProjectState()

        # Check directory structure
        state.has_ultra_dir = self._check_path(".ultra")
        state.has_specs = self._check_specs()
        state.has_tasks = self._check_tasks(state)
        state.has_research = self._check_research()
        state.has_tests = self._check_tests(state)
        state.has_uncommitted_changes = self._check_git_status()

        # Check for session recovery
        state.session_recovery = self._check_session_recovery()

        # Determine phase and suggestion
        self._determine_phase(state)

        return state

    def _check_path(self, path: str) -> bool:
        """Check if path exists."""
        return (self.project_path / path).exists()

    def _check_specs(self) -> bool:
        """Check for specification files."""
        specs_locations = [
            "specs/product.md",
            "specs/architecture.md",
            "docs/prd.md",
            "docs/tech.md"
        ]
        return any(self._check_path(loc) for loc in specs_locations)

    def _check_tasks(self, state: ProjectState) -> bool:
        """Check for tasks.json and parse task counts."""
        tasks_file = self.project_path / ".ultra" / "tasks" / "tasks.json"
        if not tasks_file.exists():
            return False

        try:
            with open(tasks_file) as f:
                data = json.load(f)
                tasks = data.get("tasks", [])
                state.tasks_total = len(tasks)
                state.tasks_completed = sum(
                    1 for t in tasks
                    if t.get("status") == "completed"
                )
                return True
        except (json.JSONDecodeError, KeyError):
            return False

    def _check_research(self) -> bool:
        """Check for research documentation."""
        research_path = self.project_path / ".ultra" / "docs" / "research"
        if not research_path.exists():
            return False
        return any(research_path.glob("*.md"))

    def _check_tests(self, state: ProjectState) -> bool:
        """Check for test files."""
        test_patterns = ["**/*.test.ts", "**/*.spec.ts", "**/*.test.js", "**/*.spec.js"]
        test_files = []
        for pattern in test_patterns:
            test_files.extend(self.project_path.glob(pattern))
        state.test_files_count = len(test_files)
        return len(test_files) > 0

    def _check_git_status(self) -> bool:
        """Check for uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True,
                cwd=self.project_path
            )
            return bool(result.stdout.strip())
        except:
            return False

    def _check_session_recovery(self) -> Optional[Dict]:
        """Check for recoverable session."""
        session_file = self.project_path / ".ultra" / "context-archive" / "session-index.json"
        if not session_file.exists():
            return None

        try:
            with open(session_file) as f:
                return json.load(f)
        except:
            return None

    def _determine_phase(self, state: ProjectState):
        """Determine current phase and suggest next command."""

        # Build completed/pending lists
        if state.has_ultra_dir:
            state.completed_items.append(".ultra/ 目录已初始化")
        else:
            state.pending_items.append("项目未初始化")

        if state.has_research:
            state.completed_items.append("研究文档已完成")

        if state.has_specs:
            state.completed_items.append("规格文档存在")

        if state.has_tasks:
            state.completed_items.append(f"任务规划完成 ({state.tasks_completed}/{state.tasks_total})")

        if state.has_tests:
            state.completed_items.append(f"测试文件 ({state.test_files_count} 个)")

        # Determine phase and suggestion
        if not state.has_ultra_dir:
            state.current_phase = "uninitialized"
            state.suggested_command = "/ultra-init"
            state.suggestion_reason = "项目需要初始化 Ultra Builder 结构"

        elif not state.has_specs:
            state.current_phase = "research"
            state.suggested_command = "/ultra-research"
            state.suggestion_reason = "需要技术调研来生成规格文档"

        elif not state.has_tasks:
            state.current_phase = "planning"
            state.suggested_command = "/ultra-plan"
            state.suggestion_reason = "规格完成，可以开始任务规划"

        elif state.tasks_completed < state.tasks_total:
            state.current_phase = "development"
            next_task = state.tasks_completed + 1
            state.suggested_command = f"/ultra-dev Task #{next_task}"
            state.suggestion_reason = f"继续开发任务 ({state.tasks_completed}/{state.tasks_total} 完成)"
            state.pending_items.append(f"剩余任务: {state.tasks_total - state.tasks_completed}")

        elif not state.has_tests or state.test_files_count < state.tasks_total:
            state.current_phase = "testing"
            state.suggested_command = "/ultra-test"
            state.suggestion_reason = "所有任务完成，需要质量验证"

        else:
            state.current_phase = "delivery"
            state.suggested_command = "/ultra-deliver"
            state.suggestion_reason = "开发和测试完成，准备交付"

        # Add warnings
        if state.has_uncommitted_changes:
            state.warnings.append("存在未提交的更改")

        if state.session_recovery:
            state.warnings.append("检测到可恢复的会话")


def format_output(state: ProjectState) -> str:
    """Format state for display."""
    lines = [
        "",
        "=" * 50,
        "项目状态分析",
        "=" * 50,
        "",
        f"当前阶段: {state.current_phase}",
        "",
    ]

    if state.completed_items:
        lines.append("已完成:")
        for item in state.completed_items:
            lines.append(f"  ✅ {item}")
        lines.append("")

    if state.pending_items:
        lines.append("待处理:")
        for item in state.pending_items:
            lines.append(f"  ⏳ {item}")
        lines.append("")

    if state.warnings:
        lines.append("警告:")
        for warning in state.warnings:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")

    if state.session_recovery:
        lines.append("会话恢复:")
        lines.append(f"  上次会话: {state.session_recovery.get('lastUpdated', 'unknown')}")
        lines.append("")

    lines.extend([
        "建议下一步:",
        f"  命令: {state.suggested_command}",
        f"  原因: {state.suggestion_reason}",
        "",
        "=" * 50
    ])

    return "\n".join(lines)


def format_json(state: ProjectState) -> str:
    """Format state as JSON."""
    return json.dumps({
        "phase": state.current_phase,
        "suggested_command": state.suggested_command,
        "suggestion_reason": state.suggestion_reason,
        "tasks": {
            "completed": state.tasks_completed,
            "total": state.tasks_total
        },
        "tests": state.test_files_count,
        "warnings": state.warnings,
        "session_recovery": state.session_recovery is not None
    }, indent=2, ensure_ascii=False)


def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    detector = ProjectStateDetector(project_path)
    state = detector.detect()

    # Check for --json flag
    if "--json" in sys.argv:
        print(format_json(state))
    else:
        print(format_output(state))


if __name__ == "__main__":
    main()
