# TDD Runner Memory - the-ai-U Agent

## Project: the-ai-U (Desktop AI Companion)

### Test Framework
- **Python Backend (Agent)**: pytest 9.0.2 with pytest-asyncio for async tests
- **Test Root**: `/Users/rocky243/testing-project/aiGFproject/the-ai-U/agent/tests/`
- **Config**: `pyproject.toml` with asyncio_mode = "auto"

### Test Modules
1. `tests/channels/test_desktop_voice.py` - Desktop voice handler tests (6 tests)
2. `tests/providers/test_transcription.py` - Groq transcription provider tests (5 tests)
3. `tests/services/test_stt_service.py` - STT service tests (9 tests)

**Total**: 20 tests, all passing

### Mock Strategy: Test Doubles for External APIs
- Uses `pytest_httpx.HTTPXMock` for mocking HTTP calls to Groq API
- **Rationale**: External API (Groq transcription) - appropriate to use test double
- No forbidden patterns detected (no InMemory*, Mock*, Fake* repositories, no jest.fn() for domain logic)

### Test Quality Notes
- All tests async with proper asyncio handling
- Good error case coverage: rate limits, missing API keys, invalid input, HTTP errors
- Tests validate: STT availability, authorization headers, empty responses, missing response fields
- No IT.skip() patterns found

### Known Issues
- Coverage reporting fails (module path configuration issue, not affecting test pass/fail)
- Project structure uses flat agent directory (services/, nanobot/, proactive/) rather than src/ subdirectory

### Recent Status (2026-02-22)
- 20/20 tests PASS
- Duration: ~5s
- No failures, no flakes detected
