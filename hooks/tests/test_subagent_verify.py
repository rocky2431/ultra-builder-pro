"""Tests for subagent_verify hook (Phase 6 v1, sensor-first).

Walking skeleton + claim parser + three verifiers. Real I/O for path /
settings checks; URL test uses a known-stable example.com to avoid
brittleness.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_DIR))

import subagent_verify  # noqa: E402


# -- helpers --

def run_hook(stdin_payload):
    """Run hook as subprocess; returns (returncode, stdout, stderr)."""
    raw = stdin_payload if isinstance(stdin_payload, str) else json.dumps(stdin_payload)
    result = subprocess.run(
        ["python3", str(HOOKS_DIR / "subagent_verify.py")],
        input=raw, capture_output=True, text=True, timeout=15,
    )
    return result.returncode, result.stdout, result.stderr


# -- extract_summary --

def test_extract_summary_uses_last_assistant_message_when_present():
    payload = {"last_assistant_message": "hello world"}
    assert subagent_verify.extract_summary(payload) == "hello world"


def test_extract_summary_returns_empty_for_missing_input():
    assert subagent_verify.extract_summary({}) == ""


def test_extract_summary_falls_back_to_transcript_file(tmp_path):
    transcript = tmp_path / "agent.jsonl"
    events = [
        {"type": "user", "message": {"content": [{"type": "text", "text": "Q"}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "draft"}]}},
        {"type": "progress", "data": {}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "final answer"}]}},
    ]
    transcript.write_text("\n".join(json.dumps(e) for e in events))
    payload = {"agent_transcript_path": str(transcript)}
    assert subagent_verify.extract_summary(payload) == "final answer"


def test_extract_summary_handles_multiple_text_blocks(tmp_path):
    transcript = tmp_path / "agent.jsonl"
    events = [{
        "type": "assistant",
        "message": {"content": [
            {"type": "text", "text": "part one"},
            {"type": "tool_use", "id": "x"},
            {"type": "text", "text": "part two"},
        ]}
    }]
    transcript.write_text("\n".join(json.dumps(e) for e in events))
    out = subagent_verify.extract_summary({"agent_transcript_path": str(transcript)})
    assert "part one" in out and "part two" in out


def test_extract_summary_returns_empty_for_missing_file():
    payload = {"agent_transcript_path": "/nonexistent/path.jsonl"}
    assert subagent_verify.extract_summary(payload) == ""


# -- parse_claims --

def test_parse_claims_extracts_urls():
    text = "Visit https://example.com and http://test.org/page for info."
    urls = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'url']
    assert "https://example.com" in urls
    assert "http://test.org/page" in urls


def test_parse_claims_strips_trailing_punctuation_from_url():
    text = "See https://example.com/page."
    urls = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'url']
    assert "https://example.com/page" in urls


def test_parse_claims_extracts_absolute_and_home_paths():
    text = "Edit ~/.claude/settings.json or /etc/hosts.conf to fix."
    paths = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'path']
    assert "~/.claude/settings.json" in paths
    assert "/etc/hosts.conf" in paths


def test_parse_claims_skips_relative_paths():
    """Relative paths (./xxx, ../xxx) are skipped: subagent's cwd is unknown,
    so we cannot tell if the file exists from our vantage point."""
    text = "Run ./install.sh or check ../config/db.yaml first."
    paths = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'path']
    assert paths == []


def test_parse_claims_url_strips_trailing_backtick():
    """Markdown-wrapped URL: `https://x.com/api` should yield clean URL."""
    text = "Endpoint: `https://app.example.com/api`"
    urls = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'url']
    assert urls == ["https://app.example.com/api"]


def test_parse_claims_field_only_when_settings_context_in_same_sentence():
    no_ctx = "The `viewMode` variable is computed."
    yes_ctx = "Set `viewMode` in settings.json to verbose."
    no_fields = [c['value'] for c in subagent_verify.parse_claims(no_ctx) if c['kind'] == 'field']
    yes_fields = [c['value'] for c in subagent_verify.parse_claims(yes_ctx) if c['kind'] == 'field']
    assert no_fields == []
    assert "viewMode" in yes_fields


def test_parse_claims_field_skips_when_settings_in_different_sentence():
    """False-positive guard: subagent intro says 'edit settings.json' once,
    then describes another repo's modules with backticks. Only same-sentence
    proximity should count."""
    text = (
        "First, open settings.json to configure. "
        "The repo has tables: `users`, `agents`, `projects` — all in Postgres."
    )
    fields = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'field']
    assert fields == []


def test_parse_claims_dedupes_repeated_urls():
    text = "Both https://a.com and https://a.com again."
    urls = [c['value'] for c in subagent_verify.parse_claims(text) if c['kind'] == 'url']
    assert urls.count("https://a.com") == 1


def test_parse_claims_empty_summary():
    assert subagent_verify.parse_claims("") == []


def test_parse_claims_url_path_not_double_matched():
    text = "Docs at https://code.claude.com/docs/en/settings.md are wrong."
    claims = subagent_verify.parse_claims(text)
    paths = [c['value'] for c in claims if c['kind'] == 'path']
    urls = [c['value'] for c in claims if c['kind'] == 'url']
    assert len(urls) == 1
    assert paths == []  # path inside URL must not be re-matched as a path


# -- verify_path --

def test_verify_path_real_file():
    assert subagent_verify.verify_path("~/.claude/settings.json") is True


def test_verify_path_fake_file():
    assert subagent_verify.verify_path("/no/such/path.xyz") is False


# -- verify_url (integration; example.com is stable per RFC 2606 test domain) --

@pytest.mark.timeout(10)
def test_verify_url_real_returns_true_or_none():
    result = subagent_verify.verify_url("https://example.com")
    assert result is True or result is None


def test_verify_url_invalid_scheme_returns_none():
    assert subagent_verify.verify_url("not-a-url") is None


# -- verify_field --

def test_verify_field_known_settings_key():
    keys = subagent_verify._load_settings_keys()
    if "permissions" in keys:
        assert subagent_verify.verify_field("permissions", keys) is True


def test_verify_field_fabricated_field_fails():
    keys = {"permissions", "hooks", "model"}
    assert subagent_verify.verify_field("viewMode", keys) is False


def test_verify_field_loads_settings_when_keys_not_provided():
    # Should not crash; either True or False depending on real settings
    result = subagent_verify.verify_field("nonexistent_xyz_999")
    assert result in (True, False)


# -- format_advisory --

def test_format_advisory_only_lists_failures():
    claims = [
        {'kind': 'url', 'value': 'https://good.com'},
        {'kind': 'url', 'value': 'https://bad.com'},
        {'kind': 'path', 'value': '/no/such/path'},
    ]
    results = [True, False, False]
    msg = subagent_verify.format_advisory("guide", claims, results)
    assert "https://good.com" not in msg
    assert "https://bad.com" in msg
    assert "/no/such/path" in msg
    assert "2 unverified" in msg


def test_format_advisory_empty_when_all_pass_or_unknown():
    claims = [{'kind': 'url', 'value': 'https://x.com'}]
    assert subagent_verify.format_advisory("g", claims, [True]) == ''
    assert subagent_verify.format_advisory("g", claims, [None]) == ''


# -- end-to-end hook invocation --

def test_hook_exits_clean_on_empty_stdin():
    rc, stdout, _ = run_hook("")
    assert rc == 0
    assert stdout.strip() == "{}"


def test_hook_exits_clean_when_no_summary():
    rc, stdout, _ = run_hook({"agent_id": "x"})
    assert rc == 0
    assert stdout.strip() == "{}"


def test_hook_exits_clean_when_summary_has_no_claims():
    rc, stdout, _ = run_hook({"last_assistant_message": "Just plain prose, no claims."})
    assert rc == 0
    assert stdout.strip() == "{}"


def test_hook_emits_advisory_for_fabricated_path():
    payload = {
        "agent_type": "guide",
        "last_assistant_message": "See /definitely/not/a/real/file.py for details.",
    }
    rc, stdout, stderr = run_hook(payload)
    assert rc == 0
    assert "[Verify]" in stderr
    assert "/definitely/not/a/real/file.py" in stderr
    out = json.loads(stdout)
    assert out["hookSpecificOutput"]["hookEventName"] == "SubagentStop"
    assert "/definitely/not/a/real/file.py" in out["hookSpecificOutput"]["additionalContext"]


def test_hook_emits_advisory_for_fabricated_settings_field():
    payload = {
        "agent_type": "guide",
        "last_assistant_message": (
            "Set `viewModeFabricated` in settings.json to enable focus mode."
        ),
    }
    rc, _, stderr = run_hook(payload)
    assert rc == 0
    assert "[Verify]" in stderr
    assert "viewModeFabricated" in stderr


def test_hook_silent_when_real_path_cited():
    payload = {
        "agent_type": "guide",
        "last_assistant_message": "See ~/.claude/settings.json for config.",
    }
    rc, stdout, stderr = run_hook(payload)
    assert rc == 0
    assert "[Verify]" not in stderr
    assert stdout.strip() == "{}"
