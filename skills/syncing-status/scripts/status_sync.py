#!/usr/bin/env python3
"""
Status Synchronization Script

Maintains feature-status.json with task completion and test results.

Usage:
    python status_sync.py record <task-id> --commit <hash> --branch <name>
    python status_sync.py test <task-id> --coverage <pct> --status <pass|fail>
    python status_sync.py check  # Consistency check
    python status_sync.py report  # Generate status report
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class FeatureStatus:
    """Status entry for a feature/task."""
    id: str
    name: str
    status: str  # pending, pass, fail
    taskId: str
    implementedAt: str
    commit: Optional[str] = None
    branch: Optional[str] = None
    testedAt: Optional[str] = None
    coverage: Optional[int] = None
    coreWebVitals: Optional[Dict] = None


class StatusManager:
    """Manages feature status tracking."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.status_file = self.project_path / ".ultra" / "docs" / "feature-status.json"
        self.tasks_file = self.project_path / ".ultra" / "tasks" / "tasks.json"
        self.log_file = self.project_path / ".ultra" / "docs" / "status-sync.log"

    def _ensure_dirs(self):
        """Ensure required directories exist."""
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_status(self) -> List[Dict]:
        """Load current status entries."""
        if not self.status_file.exists():
            return []
        try:
            with open(self.status_file) as f:
                return json.load(f)
        except:
            return []

    def _save_status(self, entries: List[Dict]):
        """Save status entries."""
        self._ensure_dirs()
        with open(self.status_file, 'w') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

    def _log(self, message: str):
        """Append to log file."""
        self._ensure_dirs()
        timestamp = datetime.now().isoformat()
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def record_completion(self, task_id: str, name: str, commit: str = None, branch: str = None):
        """Record task completion."""
        entries = self._load_status()

        # Check if already exists
        for entry in entries:
            if entry.get("taskId") == task_id:
                self._log(f"Task {task_id} already recorded, skipping")
                return entry

        new_entry = {
            "id": f"feat-{task_id}",
            "name": name,
            "status": "pending",
            "taskId": task_id,
            "implementedAt": datetime.now().isoformat(),
            "commit": commit,
            "branch": branch
        }

        entries.append(new_entry)
        self._save_status(entries)
        self._log(f"Recorded completion for task {task_id}")

        return new_entry

    def record_test_result(self, task_id: str, status: str, coverage: int = None,
                          lcp: int = None, inp: int = None, cls: float = None):
        """Record test results for a task."""
        entries = self._load_status()

        for entry in entries:
            if entry.get("taskId") == task_id:
                entry["status"] = status
                entry["testedAt"] = datetime.now().isoformat()
                if coverage is not None:
                    entry["coverage"] = coverage
                if lcp or inp or cls:
                    entry["coreWebVitals"] = {
                        "lcp": lcp,
                        "inp": inp,
                        "cls": cls
                    }
                self._save_status(entries)
                self._log(f"Recorded test result for task {task_id}: {status}")
                return entry

        self._log(f"Warning: Task {task_id} not found for test recording")
        return None

    def check_consistency(self) -> Dict:
        """Check consistency between tasks.json and feature-status.json."""
        result = {
            "missing_status": [],
            "stale_pending": [],
            "orphaned_status": [],
            "total_tasks": 0,
            "total_status": 0
        }

        # Load tasks
        tasks = []
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file) as f:
                    data = json.load(f)
                    tasks = data.get("tasks", [])
            except:
                pass

        # Load status
        status_entries = self._load_status()

        result["total_tasks"] = len(tasks)
        result["total_status"] = len(status_entries)

        # Find completed tasks without status
        completed_task_ids = {t.get("id") for t in tasks if t.get("status") == "completed"}
        status_task_ids = {e.get("taskId") for e in status_entries}

        result["missing_status"] = list(completed_task_ids - status_task_ids)

        # Find stale pending (pending > 24 hours)
        now = datetime.now()
        for entry in status_entries:
            if entry.get("status") == "pending":
                try:
                    impl_time = datetime.fromisoformat(entry.get("implementedAt", ""))
                    if (now - impl_time).days >= 1:
                        result["stale_pending"].append(entry.get("taskId"))
                except:
                    pass

        # Find orphaned status entries
        task_ids = {t.get("id") for t in tasks}
        result["orphaned_status"] = [
            e.get("taskId") for e in status_entries
            if e.get("taskId") not in task_ids
        ]

        return result

    def generate_report(self) -> str:
        """Generate status report."""
        entries = self._load_status()
        consistency = self.check_consistency()

        lines = [
            "",
            "=" * 50,
            "功能状态报告",
            "=" * 50,
            "",
            f"总任务数: {consistency['total_tasks']}",
            f"状态记录: {consistency['total_status']}",
            "",
        ]

        # Status breakdown
        status_counts = {"pass": 0, "fail": 0, "pending": 0}
        for entry in entries:
            status = entry.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

        lines.append("状态分布:")
        lines.append(f"  ✅ 通过: {status_counts.get('pass', 0)}")
        lines.append(f"  ❌ 失败: {status_counts.get('fail', 0)}")
        lines.append(f"  ⏳ 待测: {status_counts.get('pending', 0)}")

        # Issues
        if consistency["missing_status"]:
            lines.append("")
            lines.append("⚠️  缺少状态记录的任务:")
            for task_id in consistency["missing_status"]:
                lines.append(f"  - Task #{task_id}")

        if consistency["stale_pending"]:
            lines.append("")
            lines.append("⚠️  待测超过24小时:")
            for task_id in consistency["stale_pending"]:
                lines.append(f"  - Task #{task_id}")

        lines.append("")
        lines.append("=" * 50)

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python status_sync.py record <task-id> --name <name> --commit <hash>")
        print("  python status_sync.py test <task-id> --status pass --coverage 85")
        print("  python status_sync.py check")
        print("  python status_sync.py report")
        sys.exit(1)

    manager = StatusManager()
    command = sys.argv[1]

    if command == "record":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        name = ""
        commit = None
        branch = None

        for i, arg in enumerate(sys.argv):
            if arg == "--name" and i + 1 < len(sys.argv):
                name = sys.argv[i + 1]
            if arg == "--commit" and i + 1 < len(sys.argv):
                commit = sys.argv[i + 1]
            if arg == "--branch" and i + 1 < len(sys.argv):
                branch = sys.argv[i + 1]

        if task_id:
            entry = manager.record_completion(task_id, name, commit, branch)
            print(f"✅ Task #{task_id} 状态已记录")
            print(json.dumps(entry, indent=2, ensure_ascii=False))

    elif command == "test":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        status = "pending"
        coverage = None

        for i, arg in enumerate(sys.argv):
            if arg == "--status" and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
            if arg == "--coverage" and i + 1 < len(sys.argv):
                coverage = int(sys.argv[i + 1])

        if task_id:
            entry = manager.record_test_result(task_id, status, coverage)
            if entry:
                print(f"✅ Task #{task_id} 测试结果已记录: {status}")
            else:
                print(f"⚠️  Task #{task_id} 未找到")

    elif command == "check":
        result = manager.check_consistency()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "report":
        print(manager.generate_report())


if __name__ == "__main__":
    main()
