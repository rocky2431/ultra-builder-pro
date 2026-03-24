"""Tests for observation_capture.py — pattern matching + DB writes."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from observation_capture import (
    TEST_CMD_PATTERNS,
    TEST_FAIL_PATTERNS,
    SIGNIFICANT_CMD_PATTERNS,
    FILE_PATH_PATTERN,
    _extract_related_files,
)


class TestTestCmdPatterns:
    """TEST_CMD_PATTERNS should match test runners, not install commands."""

    SHOULD_MATCH = [
        "npm test",
        "npx jest --coverage",
        "yarn test -- auth.test.ts",
        "pnpm test",
        "bun test src/",
        "pytest tests/test_auth.py -v",
        "python -m unittest discover",
        "python3 -m pytest tests/",
        "cargo test --release",
        "go test ./...",
        "dotnet test MyProject.Tests",
        "mix test test/auth_test.exs",
        "flutter test test/widget_test.dart",
        "php artisan test --filter=AuthTest",
        "phpunit tests/AuthTest.php",
        "rspec spec/auth_spec.rb",
        "make test",
        "gradle test",
        "mvn test -pl auth-module",
        "jest --watchAll",
        "vitest run",
    ]

    SHOULD_NOT_MATCH = [
        "ls -la",
        "git status",
        "npm install",
        "echo test",
        "cat test.log",
    ]

    def test_matches_test_runners(self):
        for cmd in self.SHOULD_MATCH:
            assert TEST_CMD_PATTERNS.search(cmd), f"Should match: {cmd}"

    def test_rejects_non_test_commands(self):
        for cmd in self.SHOULD_NOT_MATCH:
            assert not TEST_CMD_PATTERNS.search(cmd), f"Should not match: {cmd}"


class TestTestFailPatterns:
    """TEST_FAIL_PATTERNS should detect failure indicators in output."""

    def test_detects_fail(self):
        assert TEST_FAIL_PATTERNS.search("FAIL src/auth.test.ts")

    def test_detects_error(self):
        assert TEST_FAIL_PATTERNS.search("ERROR: connection refused")

    def test_detects_assertion_error(self):
        assert TEST_FAIL_PATTERNS.search("AssertionError: expected 1 to equal 2")

    def test_detects_tests_failed(self):
        assert TEST_FAIL_PATTERNS.search("3 tests failed")

    def test_detects_panic(self):
        assert TEST_FAIL_PATTERNS.search("panic: runtime error")

    def test_ignores_normal_output(self):
        assert not TEST_FAIL_PATTERNS.search("All tests passed successfully")

    def test_ignores_info_messages(self):
        assert not TEST_FAIL_PATTERNS.search("Running 15 test suites...")


class TestSignificantCmdPatterns:
    """SIGNIFICANT_CMD_PATTERNS for git/build/deploy commands."""

    SHOULD_MATCH = [
        "git commit -m 'feat: add auth'",
        "git push origin main",
        "git merge feat/auth",
        "npm run build",
        "cargo build --release",
        "docker build -t myapp .",
        "docker compose up -d",
        "terraform apply",
        "kubectl apply -f deploy.yaml",
        "make",
        "gradle build",
        "mvn package",
    ]

    SHOULD_NOT_MATCH = [
        "ls -la",
        "git status",
        "git log --oneline",
        "git diff",
        "cat README.md",
        "echo hello",
        "python3 app.py",
        "node server.js",
    ]

    def test_matches_significant_commands(self):
        for cmd in self.SHOULD_MATCH:
            assert SIGNIFICANT_CMD_PATTERNS.search(cmd), f"Should match: {cmd}"

    def test_rejects_trivial_commands(self):
        for cmd in self.SHOULD_NOT_MATCH:
            assert not SIGNIFICANT_CMD_PATTERNS.search(cmd), f"Should not match: {cmd}"


class TestExtractRelatedFiles:
    """_extract_related_files should pull file paths from commands and output."""

    def test_extracts_test_file_from_command(self):
        files = _extract_related_files("npm test -- auth.test.ts", "")
        assert any("auth.test.ts" in f for f in files)

    def test_extracts_src_path_from_output(self):
        output = "FAIL src/auth/login.test.ts\n  at validateToken (src/auth/auth.ts:42)"
        files = _extract_related_files("npm test", output)
        assert any("src/auth" in f for f in files)

    def test_extracts_spec_file(self):
        files = _extract_related_files("rspec spec/auth_spec.rb", "")
        assert any("auth_spec.rb" in f for f in files)

    def test_empty_on_no_files(self):
        files = _extract_related_files("echo hello", "just some text")
        assert len(files) == 0

    def test_caps_at_5_files(self):
        output = "\n".join(f"FAIL src/file{i}.test.ts" for i in range(10))
        files = _extract_related_files("npm test", output)
        assert len(files) <= 5
