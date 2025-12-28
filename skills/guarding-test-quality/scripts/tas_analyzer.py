#!/usr/bin/env python3
"""
TAS (Test Authenticity Score) Analyzer

Analyzes test files for quality patterns and calculates authenticity scores.

Usage:
    python tas_analyzer.py <test-file-or-directory>
    python tas_analyzer.py src/  # Analyze all tests in directory
    python tas_analyzer.py --summary  # Project summary only
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple


@dataclass
class TestFileAnalysis:
    """Analysis results for a single test file."""
    file_path: str
    total_tests: int = 0
    assertions_count: int = 0
    mock_count: int = 0
    internal_mocks: int = 0
    external_mocks: int = 0

    # Quality indicators
    empty_tests: int = 0
    tautology_tests: int = 0
    mock_only_assertions: int = 0
    behavioral_assertions: int = 0

    # Patterns detected
    patterns: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    # TAS score components (0-100)
    mock_ratio_score: float = 0.0
    assertion_quality_score: float = 0.0
    real_execution_score: float = 0.0
    pattern_quality_score: float = 0.0
    final_score: float = 0.0
    grade: str = "F"


class TASAnalyzer:
    """Analyzes test authenticity."""

    # Patterns for detection
    TEST_PATTERNS = [
        r'(it|test|describe)\s*\(',
        r'@Test',
        r'def\s+test_',
    ]

    ASSERTION_PATTERNS = [
        r'expect\s*\(',
        r'assert',
        r'should\.',
        r'toBe|toEqual|toMatch|toContain|toThrow',
        r'assertEqual|assertTrue|assertFalse',
    ]

    MOCK_PATTERNS = [
        r'jest\.mock\(',
        r'vi\.mock\(',
        r'mock\(',
        r'createMock',
        r'@Mock',
        r'unittest\.mock',
        r'MagicMock',
    ]

    INTERNAL_MOCK_INDICATORS = [
        r'\.\./',           # Relative imports
        r'@/',              # Alias imports
        r'src/',            # Source imports
        r'services/',
        r'utils/',
        r'components/',
        r'hooks/',
    ]

    EXTERNAL_MOCK_INDICATORS = [
        r'axios',
        r'fetch',
        r'http',
        r'database',
        r'firebase',
        r'stripe',
        r'aws-sdk',
        r'@prisma',
        r'redis',
        r'mongodb',
    ]

    TAUTOLOGY_PATTERNS = [
        r'expect\s*\(\s*true\s*\)\s*\.toBe\s*\(\s*true\s*\)',
        r'expect\s*\(\s*1\s*\)\s*\.toBe\s*\(\s*1\s*\)',
        r'expect\s*\(\s*".*"\s*\)\s*\.toBe\s*\(\s*".*"\s*\)',
        r'assert\s+True',
        r'assertEqual\s*\(\s*1\s*,\s*1\s*\)',
    ]

    MOCK_ONLY_ASSERTION_PATTERNS = [
        r'toHaveBeenCalled(?!With)',
        r'toHaveBeenCalledTimes',
        r'assert_called',
        r'verify\(',
    ]

    BEHAVIORAL_ASSERTION_PATTERNS = [
        r'\.toBe\s*\(\s*[^)]+\s*\)',
        r'\.toEqual\s*\(',
        r'\.toContain\s*\(',
        r'\.toThrow\s*\(',
        r'\.toMatch\s*\(',
        r'assertEqual\s*\(',
        r'assertIn\s*\(',
    ]

    def analyze_file(self, file_path: Path) -> TestFileAnalysis:
        """Analyze a single test file."""
        analysis = TestFileAnalysis(file_path=str(file_path))

        try:
            content = file_path.read_text()
        except Exception as e:
            analysis.issues.append(f"Could not read file: {e}")
            return analysis

        lines = content.split('\n')

        # Count tests
        for pattern in self.TEST_PATTERNS:
            analysis.total_tests += len(re.findall(pattern, content))

        # Count assertions
        for pattern in self.ASSERTION_PATTERNS:
            analysis.assertions_count += len(re.findall(pattern, content, re.IGNORECASE))

        # Count mocks
        for pattern in self.MOCK_PATTERNS:
            analysis.mock_count += len(re.findall(pattern, content, re.IGNORECASE))

        # Classify mocks
        for pattern in self.INTERNAL_MOCK_INDICATORS:
            if re.search(f'mock.*{pattern}', content, re.IGNORECASE):
                analysis.internal_mocks += 1

        for pattern in self.EXTERNAL_MOCK_INDICATORS:
            if re.search(f'mock.*{pattern}', content, re.IGNORECASE):
                analysis.external_mocks += 1

        # Detect anti-patterns
        for pattern in self.TAUTOLOGY_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis.tautology_tests += len(matches)
            if matches:
                analysis.issues.append("Tautology tests detected (always pass)")

        for pattern in self.MOCK_ONLY_ASSERTION_PATTERNS:
            analysis.mock_only_assertions += len(re.findall(pattern, content))

        for pattern in self.BEHAVIORAL_ASSERTION_PATTERNS:
            analysis.behavioral_assertions += len(re.findall(pattern, content))

        # Detect empty test bodies
        empty_test_pattern = r'(it|test)\s*\([^)]+\)\s*=>\s*\{\s*\}'
        analysis.empty_tests = len(re.findall(empty_test_pattern, content))
        if analysis.empty_tests:
            analysis.issues.append(f"{analysis.empty_tests} empty test bodies")

        # Calculate scores
        self._calculate_scores(analysis)

        # Generate suggestions
        self._generate_suggestions(analysis)

        return analysis

    def _calculate_scores(self, analysis: TestFileAnalysis):
        """Calculate TAS score components."""

        # 1. Mock Ratio Score (25%)
        # Lower internal mocks = higher score
        if analysis.mock_count > 0:
            internal_ratio = analysis.internal_mocks / analysis.mock_count
            analysis.mock_ratio_score = max(0, 100 - (internal_ratio * 150))
        else:
            analysis.mock_ratio_score = 100

        # 2. Assertion Quality Score (35%)
        # Higher behavioral assertions = higher score
        if analysis.assertions_count > 0:
            behavioral_ratio = analysis.behavioral_assertions / analysis.assertions_count
            mock_only_penalty = (analysis.mock_only_assertions / analysis.assertions_count) * 50
            analysis.assertion_quality_score = max(0, (behavioral_ratio * 100) - mock_only_penalty)
        else:
            analysis.assertion_quality_score = 0

        # 3. Real Execution Score (25%)
        # Based on assertion density per test
        if analysis.total_tests > 0:
            assertions_per_test = analysis.assertions_count / analysis.total_tests
            analysis.real_execution_score = min(100, assertions_per_test * 25)
        else:
            analysis.real_execution_score = 0

        # 4. Pattern Quality Score (15%)
        # Penalize anti-patterns
        penalty = 0
        if analysis.empty_tests > 0:
            penalty += 30
        if analysis.tautology_tests > 0:
            penalty += 40
        analysis.pattern_quality_score = max(0, 100 - penalty)

        # Calculate final weighted score
        analysis.final_score = (
            analysis.mock_ratio_score * 0.25 +
            analysis.assertion_quality_score * 0.35 +
            analysis.real_execution_score * 0.25 +
            analysis.pattern_quality_score * 0.15
        )

        # Assign grade
        if analysis.final_score >= 85:
            analysis.grade = "A"
        elif analysis.final_score >= 70:
            analysis.grade = "B"
        elif analysis.final_score >= 50:
            analysis.grade = "C"
        elif analysis.final_score >= 30:
            analysis.grade = "D"
        else:
            analysis.grade = "F"

    def _generate_suggestions(self, analysis: TestFileAnalysis):
        """Generate improvement suggestions."""

        if analysis.internal_mocks > analysis.external_mocks:
            analysis.suggestions.append(
                "Reduce internal mocks. Use real implementations for services and utils."
            )

        if analysis.mock_only_assertions > analysis.behavioral_assertions:
            analysis.suggestions.append(
                "Add behavioral assertions (toBe, toEqual) not just mock call checks."
            )

        if analysis.assertions_count / max(1, analysis.total_tests) < 2:
            analysis.suggestions.append(
                "Add more assertions per test. Aim for 2+ meaningful assertions."
            )

        if analysis.empty_tests > 0:
            analysis.suggestions.append(
                "Fill in empty test bodies with actual test logic."
            )

        if analysis.tautology_tests > 0:
            analysis.suggestions.append(
                "Remove tautology tests (expect(true).toBe(true)). Test real behavior."
            )

    def analyze_directory(self, dir_path: Path) -> List[TestFileAnalysis]:
        """Analyze all test files in directory."""
        results = []
        test_patterns = ["**/*.test.ts", "**/*.spec.ts", "**/*.test.js",
                        "**/*.spec.js", "**/*_test.py", "**/test_*.py"]

        for pattern in test_patterns:
            for file_path in dir_path.glob(pattern):
                if "node_modules" not in str(file_path):
                    results.append(self.analyze_file(file_path))

        return results


def format_file_report(analysis: TestFileAnalysis) -> str:
    """Format single file analysis."""
    lines = [
        f"\n{'─'*50}",
        f"文件: {analysis.file_path}",
        f"{'─'*50}",
        f"",
        f"TAS 分数: {analysis.final_score:.1f}% (等级: {analysis.grade})",
        f"",
        f"指标:",
        f"  测试数量: {analysis.total_tests}",
        f"  断言数量: {analysis.assertions_count}",
        f"  Mock 数量: {analysis.mock_count} (内部: {analysis.internal_mocks}, 外部: {analysis.external_mocks})",
        f"",
        f"分项得分:",
        f"  Mock 比例 (25%): {analysis.mock_ratio_score:.1f}",
        f"  断言质量 (35%): {analysis.assertion_quality_score:.1f}",
        f"  真实执行 (25%): {analysis.real_execution_score:.1f}",
        f"  模式质量 (15%): {analysis.pattern_quality_score:.1f}",
    ]

    if analysis.issues:
        lines.append("")
        lines.append("问题:")
        for issue in analysis.issues:
            lines.append(f"  ⚠️  {issue}")

    if analysis.suggestions:
        lines.append("")
        lines.append("改进建议:")
        for suggestion in analysis.suggestions:
            lines.append(f"  → {suggestion}")

    return "\n".join(lines)


def format_summary(results: List[TestFileAnalysis]) -> str:
    """Format project summary."""
    if not results:
        return "未找到测试文件"

    total_tests = sum(r.total_tests for r in results)
    total_assertions = sum(r.assertions_count for r in results)
    avg_score = sum(r.final_score for r in results) / len(results)

    grade_counts = {}
    for r in results:
        grade_counts[r.grade] = grade_counts.get(r.grade, 0) + 1

    # Determine overall grade
    if avg_score >= 85:
        overall_grade = "A"
    elif avg_score >= 70:
        overall_grade = "B"
    elif avg_score >= 50:
        overall_grade = "C"
    elif avg_score >= 30:
        overall_grade = "D"
    else:
        overall_grade = "F"

    lines = [
        "",
        "=" * 50,
        "📊 测试质量分析报告",
        "=" * 50,
        "",
        f"项目 TAS 分数: {avg_score:.1f}% (等级: {overall_grade})",
        "",
        "分析摘要:",
        f"  测试文件: {len(results)} 个",
        f"  测试用例: {total_tests} 个",
        f"  总断言数: {total_assertions} 个",
        f"  平均断言数: {total_assertions/max(1,total_tests):.1f} 个/测试",
        "",
        "等级分布:",
    ]

    for grade in ["A", "B", "C", "D", "F"]:
        count = grade_counts.get(grade, 0)
        if count > 0:
            lines.append(f"  {grade}: {count} 个文件")

    # Add overall suggestions
    common_issues = []
    for r in results:
        common_issues.extend(r.issues)

    if common_issues:
        lines.append("")
        lines.append("常见问题:")
        for issue in set(common_issues):
            lines.append(f"  ⚠️  {issue}")

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tas_analyzer.py <test-file-or-directory>")
        sys.exit(1)

    target = Path(sys.argv[1]) if sys.argv[1] != "--summary" else Path(".")
    summary_only = "--summary" in sys.argv

    analyzer = TASAnalyzer()

    if target.is_file():
        analysis = analyzer.analyze_file(target)
        print(format_file_report(analysis))
    else:
        results = analyzer.analyze_directory(target)
        print(format_summary(results))

        if not summary_only:
            for analysis in results:
                print(format_file_report(analysis))


if __name__ == "__main__":
    main()
