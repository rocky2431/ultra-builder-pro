"""Shared fixtures and helpers for hook tests.

Memory归位 (2026-06-02): the memory_conn / seeded_conn SQLite fixtures were
removed along with memory.db (claude-mem now owns cross-session memory).
"""
import json
import sys
from pathlib import Path

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_DIR))


def make_hook_input(**kwargs):
    """Build a hook stdin JSON payload."""
    return json.dumps(kwargs)
