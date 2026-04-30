# Enabling Templates

Starter templates that make the right path the cheap path. Referenced by `forbidden_patterns` advisories so agents have a concrete alternative to copy instead of looking for loopholes.

| Template | When to copy |
|----------|--------------|
| [testcontainer-postgres.ts](testcontainer-postgres.ts) | Need real Postgres in TS/Node tests (replaces `jest.fn()` Repository mocks) |
| [testcontainer-postgres.py](testcontainer-postgres.py) | Need real Postgres in pytest (replaces `MagicMock` Repository) |
| [vertical-slice.ts](vertical-slice.ts) | Prove HTTP→use case→DB→response works end-to-end |
| [persistence-real.ts](persistence-real.ts) | Build a Repository that actually talks to a DB (no in-memory `Map`) |
| [feature-flag-default-audit.sh](feature-flag-default-audit.sh) | Surface every `default off` / `enabled: false` so they don't hide unfinished work |

## How they're surfaced

`post_edit_guard.py` writes advisories like:
```
[MOCK:ADVISORY] foo.test.ts:42 jest.fn() for internal code → see .ultra/templates/testcontainer-*
```

The agent reads the pointer, copies the template, and ships real persistence instead of a fake.

## Adding a template

Each template MUST:
1. Be runnable as-is in a fresh project (drop in, install deps, run tests)
2. Have a comment header listing required deps and the exact command to verify
3. Be under ~80 lines (long templates get skipped)
4. Reference its rationale in `.ultra/PHILOSOPHY.md` (which commandment it serves)
