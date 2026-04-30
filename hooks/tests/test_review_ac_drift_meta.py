"""Metadata tests for review-ac-drift agent (Phase 4).

These verify the agent is wired into the ultra-review pipeline correctly.
Behavior tests require actually running /ultra-review against a real diff
and are not in scope for this suite.
"""
import re
from pathlib import Path

CLAUDE_DIR = Path(__file__).parent.parent.parent
AGENT_FILE = CLAUDE_DIR / "agents" / "review-ac-drift.md"
SKILL_FILE = CLAUDE_DIR / "skills" / "ultra-review" / "SKILL.md"
SCHEMA_FILE = CLAUDE_DIR / "skills" / "ultra-review" / "references" / "unified-schema.md"


def _parse_frontmatter(text: str) -> dict:
    """Tiny YAML frontmatter parser — assumes flat key:value (no nesting we
    care about beyond multi-line description). Avoids adding pyyaml dep."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    raw = m.group(1)
    fields: dict = {}
    current_key = None
    for line in raw.split("\n"):
        if not line.strip():
            continue
        # Top-level key:value
        kv = re.match(r"^([A-Za-z_-]+)\s*:\s*(.*)$", line)
        if kv:
            current_key = kv.group(1)
            value = kv.group(2).rstrip()
            fields[current_key] = value
        elif line.startswith("  ") and current_key:
            # continuation (e.g. multi-line description with |)
            fields[current_key] = (fields.get(current_key, "") + " " + line.strip()).strip()
    return fields


class TestAgentFile:
    def test_agent_file_exists(self):
        assert AGENT_FILE.exists(), f"missing {AGENT_FILE}"

    def test_frontmatter_has_required_fields(self):
        text = AGENT_FILE.read_text()
        fm = _parse_frontmatter(text)
        assert fm.get("name") == "review-ac-drift"
        assert "description" in fm and fm["description"]
        assert fm.get("model"), "model field missing"
        assert "tools" in fm

    def test_agent_describes_semantic_drift(self):
        text = AGENT_FILE.read_text()
        # Spot-check the agent body explicitly states its job is semantic
        # alignment (not structural — that's review-code's territory)
        assert "semantic" in text.lower()
        assert "alignment" in text.lower() or "drift" in text.lower()

    def test_writes_unified_schema_json(self):
        text = AGENT_FILE.read_text()
        # Must reference the unified schema and the OUTPUT_FILE convention
        assert "ultra-review-findings-v1" in text
        assert "OUTPUT_FILE" in text
        assert "review-ac-drift" in text  # must self-name in output


class TestSkillIntegration:
    def test_skill_md_references_agent(self):
        text = SKILL_FILE.read_text()
        assert "review-ac-drift" in text

    def test_skill_md_lists_agent_with_skip_condition(self):
        text = SKILL_FILE.read_text()
        # The auto-skip table in Phase 2 must include review-ac-drift
        agent_table_section = text.split("Mode: `full` (default)")[1].split("Mode:")[0]
        assert "review-ac-drift" in agent_table_section
        # Skip condition should mention .ultra/tasks
        assert ".ultra/tasks" in agent_table_section

    def test_skill_md_count_updated(self):
        text = SKILL_FILE.read_text()
        # Description in frontmatter says "7 specialized agents" now
        assert "7 specialized agents" in text


class TestSchemaIntegration:
    def test_agent_listed_in_schema(self):
        text = SCHEMA_FILE.read_text()
        assert "review-ac-drift" in text

    def test_categories_extended_for_agent(self):
        text = SCHEMA_FILE.read_text()
        # spec-compliance and scope-drift category rows should now mention
        # review-ac-drift (since the agent uses these categories)
        sc_row = [l for l in text.split("\n") if "spec-compliance" in l]
        assert sc_row, "spec-compliance row missing in schema"
        assert any("review-ac-drift" in r for r in sc_row), \
            "spec-compliance row should list review-ac-drift"
