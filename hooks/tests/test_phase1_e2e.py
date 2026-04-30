"""End-to-end test for Phase 1 (GAP 1 reverse trace).

Exercises the actual hook scripts via subprocess:
  1. relations_sync.py reads .ultra/tasks → writes relations.json with files index
  2. post_edit_guard.py reads relations.json → injects [Trace] to stderr

Real git repo, real subprocess, real stdin/stdout — no mocks.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_DIR = Path(__file__).parent.parent
REL_SYNC = HOOK_DIR / "relations_sync.py"
POST_EDIT = HOOK_DIR / "post_edit_guard.py"


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)


def _run_hook(script: Path, payload: dict, cwd: Path):
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc.stdout, proc.stderr, proc.returncode


@pytest.fixture
def fake_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)

    ultra = repo / ".ultra"
    (ultra / "tasks" / "contexts").mkdir(parents=True)
    (ultra / "specs").mkdir(parents=True)

    (ultra / "specs" / "product.md").write_text(
        "## VIP shipping\n\nVIP users get free shipping.\n"
    )
    (ultra / "tasks" / "tasks.json").write_text(json.dumps({
        "version": "4.4",
        "tasks": [{
            "id": "1",
            "title": "VIP shipping",
            "status": "in_progress",
            "context_file": "contexts/task-1.md",
            "trace_to": ".ultra/specs/product.md#vip-shipping",
        }],
    }))
    (ultra / "tasks" / "contexts" / "task-1.md").write_text(
        "# Task 1: VIP shipping\n\n"
        "## Implementation\n"
        "**Target Files**:\n"
        "- `src/checkout/shipping.ts` (modify)\n"
        "\n"
        "**Pattern**: existing\n"
        "## Acceptance Criteria\n"
        "- AC-1: VIP user shipping fee = 0\n"
        "- AC-2: Non-VIP user normal rate\n"
    )

    (repo / "src" / "checkout").mkdir(parents=True)
    (repo / "src" / "checkout" / "shipping.ts").write_text(
        "export function calcShipping(user) {\n"
        "  return user.isVIP ? 0 : 10;\n"
        "}\n"
    )
    return repo


def test_relations_sync_builds_files_index(fake_repo):
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(fake_repo / ".ultra" / "tasks" / "tasks.json")},
    }
    _stdout, stderr, code = _run_hook(REL_SYNC, payload, fake_repo)
    assert code == 0, f"hook exited {code}; stderr={stderr!r}"

    relations_path = fake_repo / ".ultra" / "relations.json"
    assert relations_path.exists(), "relations.json not written"

    rel = json.loads(relations_path.read_text())
    assert rel["version"] == 2
    assert "files" in rel
    assert "src/checkout/shipping.ts" in rel["files"]

    entry = rel["files"]["src/checkout/shipping.ts"]
    assert entry["tasks"] == ["1"]
    assert entry["from"] == ["target_files"]


def test_post_edit_guard_injects_trace(fake_repo):
    sync_payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(fake_repo / ".ultra" / "tasks" / "tasks.json")},
    }
    _run_hook(REL_SYNC, sync_payload, fake_repo)

    edit_payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(fake_repo / "src" / "checkout" / "shipping.ts")},
    }
    _stdout, stderr, code = _run_hook(POST_EDIT, edit_payload, fake_repo)

    assert code == 0, f"hook exited {code}; stderr={stderr!r}"
    assert "[Trace]" in stderr, f"missing [Trace]: {stderr!r}"
    assert "task-1" in stderr
    assert "VIP shipping" in stderr
    assert "AC-1" in stderr
    assert "AC-2" in stderr
    assert "in_progress" in stderr


def test_post_edit_guard_falls_back_for_unowned_file(fake_repo):
    """Phase 5C: in an Ultra project, a file that no task owns still gets a
    git-context fallback line — so the agent always has situational awareness.
    Previously this case was silent."""
    sync_payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(fake_repo / ".ultra" / "tasks" / "tasks.json")},
    }
    _run_hook(REL_SYNC, sync_payload, fake_repo)

    (fake_repo / "src" / "unrelated.ts").write_text("export const x = 1;\n")
    edit_payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(fake_repo / "src" / "unrelated.ts")},
    }
    _stdout, stderr, code = _run_hook(POST_EDIT, edit_payload, fake_repo)
    assert code == 0
    assert "[Trace] (no task)" in stderr
    assert "unrelated.ts" in stderr
    # Must NOT mistakenly attribute to an existing task
    assert "task-1" not in stderr
