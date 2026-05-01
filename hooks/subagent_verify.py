#!/usr/bin/env python3
"""
Subagent Output Verifier - SubagentStop hook (Phase 6 v1, sensor-first).

Verifies factual claims (URLs, file paths, settings fields) cited in a
subagent's final summary against ground truth. Unverified claims emit a
[Verify] advisory to stderr; the main agent decides whether to trust the
summary, re-query, or escalate. This hook never blocks (sensor mode).

Origin: 2026-05-01 transcript-view incident — a claude-code-guide subagent
fabricated four claims (viewMode field, /focus command, doc URL, option
enum). All four were plausible but wrong. Phase 6 closes this trust gap
with a deterministic, programmatic check that complements (not replaces)
the existing /ultra-verify three-way AI mitigation.

v1 scope (decided 2026-05-02):
  - URL existence (HEAD request)
  - file path existence (os.path.exists)
  - settings.json field name (auto-discovered keys)
Deferred to v2: git commit hashes, function/class names.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from hook_utils import update_task_progress
except Exception:  # pragma: no cover — never crash hook on import error
    def update_task_progress(*_args, **_kwargs):  # type: ignore[no-redef]
        return


URL_TIMEOUT_S = 3
URL_BUDGET_PER_RUN = 5


# -- Claim extraction --

URL_RE = re.compile(r'https?://[^\s<>"\'\)\]`]+')

PATH_RE = re.compile(
    r'(?<![\w/:.])(?:~)?/[\w./\-]+'
    r'\.(?:py|ts|tsx|js|jsx|json|md|toml|yaml|yml|sh|html|css|txt|conf)\b'
)

FIELD_RE = re.compile(r'`([a-zA-Z][a-zA-Z0-9_.]{1,38})`')

SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+|\n+')

SETTINGS_FILE_RE = re.compile(r'settings\.json', re.IGNORECASE)


def extract_summary(hook_input):
    """Extract subagent's final assistant text from SubagentStop input.

    Order of preference:
      1. ``last_assistant_message`` field (string) — provided by harness.
      2. ``agent_transcript_path`` — read jsonl, concat last assistant
         message's text content blocks.

    Returns empty string if neither yields content.
    """
    msg = hook_input.get('last_assistant_message', '')
    if isinstance(msg, str) and msg.strip():
        return msg

    transcript = hook_input.get('agent_transcript_path', '')
    if not transcript or not os.path.isfile(transcript):
        return ''

    last_assistant = None
    try:
        with open(transcript, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get('type') == 'assistant':
                    last_assistant = event
    except OSError:
        return ''

    if not last_assistant:
        return ''

    content = last_assistant.get('message', {}).get('content', [])
    if not isinstance(content, list):
        return ''

    chunks = []
    for item in content:
        if isinstance(item, dict) and item.get('type') == 'text':
            text = item.get('text', '')
            if isinstance(text, str):
                chunks.append(text)
    return '\n'.join(chunks)


def parse_claims(summary):
    """Extract URL / path / field claims from a summary text.

    Returns a list of dicts with kind in {url, path, field} and value.
    Deduplicated. Field claims only fire when the summary mentions
    settings.json / schema / config — otherwise backticks are too noisy
    (any code identifier would qualify).
    """
    if not summary:
        return []

    claims = []
    seen = set()

    for match in URL_RE.finditer(summary):
        value = match.group(0).rstrip('.,;:)')
        key = ('url', value)
        if key not in seen:
            seen.add(key)
            claims.append({'kind': 'url', 'value': value})

    for match in PATH_RE.finditer(summary):
        value = match.group(0)
        key = ('path', value)
        if key not in seen:
            seen.add(key)
            claims.append({'kind': 'path', 'value': value})

    # Field claims: per-sentence proximity. Only check ``backtick`` identifiers
    # in a sentence that explicitly names settings.json — otherwise every
    # code identifier in the summary becomes a false-positive (e.g. subagent
    # describing a different repo's table names like `users`, `agents`).
    for sentence in SENTENCE_SPLIT_RE.split(summary):
        if not SETTINGS_FILE_RE.search(sentence):
            continue
        for match in FIELD_RE.finditer(sentence):
            value = match.group(1)
            key = ('field', value)
            if key not in seen:
                seen.add(key)
                claims.append({'kind': 'field', 'value': value})

    return claims


# -- Verifiers (task #2: filled in below) --

def verify_path(value):
    """True if path exists on disk; False otherwise. ``~`` is expanded."""
    expanded = os.path.expanduser(value)
    return os.path.exists(expanded)


def verify_url(value):
    """HEAD-request the URL with a 3s timeout.

    Returns True for 2xx/3xx, False for 4xx, None for transient/network
    errors (fail-open — verifier should not punish flaky networks).
    """
    try:
        req = urllib.request.Request(value, method='HEAD')
        with urllib.request.urlopen(req, timeout=URL_TIMEOUT_S) as resp:
            return 200 <= resp.status < 400
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500:
            return False
        return None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None


def _load_settings_keys():
    """Recursively flatten ~/.claude/settings.json keys.

    Returns a set of dotted key paths (e.g. {'permissions', 'permissions.allow'})
    so a verifier claim of ``permissions.allow`` matches even if the field is
    nested. Empty set on any read/parse failure.
    """
    settings_path = Path.home() / '.claude' / 'settings.json'
    if not settings_path.exists():
        return set()
    try:
        data = json.loads(settings_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return set()

    keys = set()

    def _walk(obj, prefix=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                full = f"{prefix}.{k}" if prefix else k
                keys.add(k)
                keys.add(full)
                _walk(v, full)

    _walk(data)
    return keys


def verify_field(value, settings_keys=None):
    """True if ``value`` is a key in ~/.claude/settings.json (any nesting)."""
    if settings_keys is None:
        settings_keys = _load_settings_keys()
    return value in settings_keys


# -- Output --

def format_advisory(agent_type, claims, results):
    """Build a multi-line stderr advisory for unverified claims.

    Only failures (False results) are reported — None (couldn't verify) and
    True (verified) stay silent to minimize noise.
    """
    failed = [
        (c, r) for c, r in zip(claims, results) if r is False
    ]
    if not failed:
        return ''

    header = (
        f"[Verify] subagent {agent_type or '?'} cited "
        f"{len(claims)} claim(s), {len(failed)} unverified:"
    )
    lines = [header]
    for claim, _ in failed:
        kind = claim['kind']
        value = claim['value']
        if kind == 'url':
            lines.append(f"  ✗ URL not reachable: {value}")
        elif kind == 'path':
            lines.append(f"  ✗ Path not found: {value}")
        elif kind == 'field':
            lines.append(f"  ✗ Field not in settings.json: {value}")
        else:
            lines.append(f"  ✗ {kind}: {value}")
    lines.append(
        "  → Treat this summary as hypothesis, not fact. "
        "Re-query or /ultra-verify before acting."
    )
    return '\n'.join(lines)


# -- Main --

def main():
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw) if raw.strip() else {}
        if not isinstance(hook_input, dict):
            hook_input = {}
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    summary = extract_summary(hook_input)
    if not summary:
        print(json.dumps({}))
        return

    claims = parse_claims(summary)
    if not claims:
        print(json.dumps({}))
        return

    settings_keys = _load_settings_keys()
    url_count = 0
    results = []
    for claim in claims:
        kind = claim['kind']
        value = claim['value']
        if kind == 'url':
            if url_count >= URL_BUDGET_PER_RUN:
                results.append(None)
                continue
            url_count += 1
            results.append(verify_url(value))
        elif kind == 'path':
            results.append(verify_path(value))
        elif kind == 'field':
            results.append(verify_field(value, settings_keys))
        else:
            results.append(None)

    advisory = format_advisory(hook_input.get('agent_type', ''), claims, results)
    if advisory:
        print(advisory, file=sys.stderr)
        try:
            update_task_progress('<subagent>', advisories=[advisory])
        except Exception:
            pass
        result = {
            "hookSpecificOutput": {
                "hookEventName": "SubagentStop",
                "additionalContext": advisory,
            }
        }
        print(json.dumps(result))
    else:
        print(json.dumps({}))


if __name__ == '__main__':
    main()
