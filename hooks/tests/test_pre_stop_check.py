"""Tests for pre_stop_check.py — stop check logic."""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from pre_stop_check import (
    COMPLIANCE_CHECKLIST,
    get_stop_count,
    increment_stop_count,
    check_workflow_state,
    MAX_STOP_BLOCKS,
)


class TestStopCounter:
    """Stop count tracking via temp files."""

    def test_initial_count_is_zero(self):
        count = get_stop_count("test-session-nonexistent")
        assert count == 0

    def test_increment_returns_new_count(self):
        sid = f"test-stop-{os.getpid()}"
        count = increment_stop_count(sid)
        assert count == 1
        count = increment_stop_count(sid)
        assert count == 2
        # Cleanup
        path = os.path.join(tempfile.gettempdir(), f".claude_stop_count_{sid}")
        os.unlink(path)

    def test_circuit_breaker_threshold(self):
        assert MAX_STOP_BLOCKS == 2


class TestCheckWorkflowState:
    """check_workflow_state: reads .ultra/workflow-state.json."""

    def test_returns_none_when_no_file(self, tmp_path):
        with patch("pre_stop_check.get_git_toplevel", return_value=str(tmp_path)):
            result = check_workflow_state()
            assert result is None

    def test_returns_none_when_completed(self, tmp_path):
        ultra_dir = tmp_path / ".ultra"
        ultra_dir.mkdir()
        state_file = ultra_dir / "workflow-state.json"
        state_file.write_text(json.dumps({
            "command": "ultra-dev", "step": "6", "status": "committed"
        }))
        with patch("pre_stop_check.get_git_toplevel", return_value=str(tmp_path)):
            result = check_workflow_state()
            assert result is None

    def test_returns_message_when_incomplete(self, tmp_path):
        ultra_dir = tmp_path / ".ultra"
        ultra_dir.mkdir()
        state_file = ultra_dir / "workflow-state.json"
        state_file.write_text(json.dumps({
            "command": "ultra-dev", "step": "3.3", "status": "tdd_complete"
        }))
        with patch("pre_stop_check.get_git_toplevel", return_value=str(tmp_path)):
            result = check_workflow_state()
            assert result is not None
            assert "ultra-dev" in result
            assert "3.3" in result


class TestComplianceChecklist:
    """The compliance checklist should contain key anti-excuse patterns."""

    def test_contains_goal_check(self):
        assert "Goal Check" in COMPLIANCE_CHECKLIST

    def test_contains_verification(self):
        assert "Verification" in COMPLIANCE_CHECKLIST

    def test_contains_invalid_excuses(self):
        assert "diminishing returns" in COMPLIANCE_CHECKLIST
        assert "broader architectural" in COMPLIANCE_CHECKLIST
        assert "beyond the scope" in COMPLIANCE_CHECKLIST
        assert "should work" in COMPLIANCE_CHECKLIST

    def test_contains_task_list_check(self):
        assert "TaskList" in COMPLIANCE_CHECKLIST
