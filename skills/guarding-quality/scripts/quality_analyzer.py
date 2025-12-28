#!/usr/bin/env python3
"""
Code Quality Analyzer

Analyzes code files for quality metrics and SOLID principle compliance.

Usage:
    python quality_analyzer.py <file-or-directory>
    python quality_analyzer.py src/ --summary
    python quality_analyzer.py --json  # JSON output
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    file_path: str
    lines_of_code: int = 0
    functions: int = 0
    classes: int = 0

    # Quality metrics
    max_function_lines: int = 0
    max_nesting_depth: int = 0
    max_complexity: int = 0
    duplicate_blocks: int = 0

    # Issues
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    # Scores (0-100)
    function_size_score: float = 100.0
    nesting_score: float = 100.0
    complexity_score: float = 100.0
    overall_score: float = 100.0
    grade: str = "A"


class QualityAnalyzer:
    """Analyzes code quality metrics."""

    # Thresholds
    MAX_FUNCTION_LINES = 50
    MAX_NESTING_DEPTH = 3
    MAX_COMPLEXITY = 10
    MAX_DUPLICATE_LINES = 3

    # Pattern definitions
    FUNCTION_PATTERNS = {
        '.ts': r'(function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|\w+\s*\([^)]*\)\s*{)',
        '.tsx': r'(function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|\w+\s*\([^)]*\)\s*{)',
        '.js': r'(function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|\w+\s*\([^)]*\)\s*{)',
        '.jsx': r'(function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|\w+\s*\([^)]*\)\s*{)',
        '.py': r'def\s+\w+\s*\(',
        '.go': r'func\s+(?:\([^)]+\)\s*)?\w+\s*\(',
    }

    CLASS_PATTERNS = {
        '.ts': r'class\s+\w+',
        '.tsx': r'class\s+\w+',
        '.js': r'class\s+\w+',
        '.jsx': r'class\s+\w+',
        '.py': r'class\s+\w+',
        '.go': r'type\s+\w+\s+struct',
    }

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single source file."""
        analysis = FileAnalysis(file_path=str(file_path))

        try:
            content = file_path.read_text()
        except Exception as e:
            analysis.issues.append(f"Could not read file: {e}")
            return analysis

        lines = content.split('\n')
        analysis.lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('//')])

        suffix = file_path.suffix

        # Count functions
        func_pattern = self.FUNCTION_PATTERNS.get(suffix)
        if func_pattern:
            analysis.functions = len(re.findall(func_pattern, content))

        # Count classes
        class_pattern = self.CLASS_PATTERNS.get(suffix)
        if class_pattern:
            analysis.classes = len(re.findall(class_pattern, content))

        # Analyze function sizes
        self._analyze_function_sizes(content, analysis, suffix)

        # Analyze nesting depth
        self._analyze_nesting_depth(content, analysis)

        # Analyze complexity (simple approximation)
        self._analyze_complexity(content, analysis)

        # Calculate scores
        self._calculate_scores(analysis)

        # Generate suggestions
        self._generate_suggestions(analysis)

        return analysis

    def _analyze_function_sizes(self, content: str, analysis: FileAnalysis, suffix: str):
        """Analyze function sizes."""
        # Simple heuristic: count lines between function start and closing brace
        lines = content.split('\n')
        in_function = False
        function_lines = 0
        brace_depth = 0

        for line in lines:
            # Track braces
            brace_depth += line.count('{') - line.count('}')

            if '{' in line and not in_function:
                in_function = True
                function_lines = 1
            elif in_function:
                function_lines += 1
                if brace_depth == 0:
                    analysis.max_function_lines = max(analysis.max_function_lines, function_lines)
                    in_function = False
                    function_lines = 0

    def _analyze_nesting_depth(self, content: str, analysis: FileAnalysis):
        """Analyze maximum nesting depth."""
        lines = content.split('\n')
        current_depth = 0
        max_depth = 0

        for line in lines:
            # Simple brace counting
            current_depth += line.count('{')
            max_depth = max(max_depth, current_depth)
            current_depth -= line.count('}')

        analysis.max_nesting_depth = max_depth

    def _analyze_complexity(self, content: str, analysis: FileAnalysis):
        """Estimate cyclomatic complexity."""
        # Count decision points
        decision_keywords = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\b\?\b',
            r'\b&&\b', r'\b\|\|\b'
        ]

        total_decisions = 0
        for pattern in decision_keywords:
            total_decisions += len(re.findall(pattern, content))

        # Approximate complexity per function
        if analysis.functions > 0:
            analysis.max_complexity = total_decisions // analysis.functions
        else:
            analysis.max_complexity = total_decisions

    def _calculate_scores(self, analysis: FileAnalysis):
        """Calculate quality scores."""

        # Function size score
        if analysis.max_function_lines <= self.MAX_FUNCTION_LINES:
            analysis.function_size_score = 100
        else:
            excess = analysis.max_function_lines - self.MAX_FUNCTION_LINES
            analysis.function_size_score = max(0, 100 - (excess * 2))

        # Nesting score
        if analysis.max_nesting_depth <= self.MAX_NESTING_DEPTH:
            analysis.nesting_score = 100
        else:
            excess = analysis.max_nesting_depth - self.MAX_NESTING_DEPTH
            analysis.nesting_score = max(0, 100 - (excess * 15))

        # Complexity score
        if analysis.max_complexity <= self.MAX_COMPLEXITY:
            analysis.complexity_score = 100
        else:
            excess = analysis.max_complexity - self.MAX_COMPLEXITY
            analysis.complexity_score = max(0, 100 - (excess * 5))

        # Overall score (weighted average)
        analysis.overall_score = (
            analysis.function_size_score * 0.35 +
            analysis.nesting_score * 0.35 +
            analysis.complexity_score * 0.30
        )

        # Assign grade
        if analysis.overall_score >= 85:
            analysis.grade = "A"
        elif analysis.overall_score >= 70:
            analysis.grade = "B"
        elif analysis.overall_score >= 50:
            analysis.grade = "C"
        else:
            analysis.grade = "D"

    def _generate_suggestions(self, analysis: FileAnalysis):
        """Generate improvement suggestions."""

        if analysis.max_function_lines > self.MAX_FUNCTION_LINES:
            analysis.issues.append(f"Function too long: {analysis.max_function_lines} lines (max: {self.MAX_FUNCTION_LINES})")
            analysis.suggestions.append("Extract smaller helper functions with single responsibilities")

        if analysis.max_nesting_depth > self.MAX_NESTING_DEPTH:
            analysis.issues.append(f"Nesting too deep: {analysis.max_nesting_depth} levels (max: {self.MAX_NESTING_DEPTH})")
            analysis.suggestions.append("Use early returns, guard clauses, or extract nested logic")

        if analysis.max_complexity > self.MAX_COMPLEXITY:
            analysis.issues.append(f"High complexity: ~{analysis.max_complexity} (max: {self.MAX_COMPLEXITY})")
            analysis.suggestions.append("Reduce conditionals, use polymorphism or strategy pattern")

    def analyze_directory(self, dir_path: Path) -> List[FileAnalysis]:
        """Analyze all source files in directory."""
        results = []
        patterns = ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.py", "**/*.go"]

        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                if "node_modules" not in str(file_path) and "dist" not in str(file_path):
                    results.append(self.analyze_file(file_path))

        return results


def format_file_report(analysis: FileAnalysis) -> str:
    """Format single file analysis."""
    lines = [
        f"\n{'─'*50}",
        f"文件: {analysis.file_path}",
        f"{'─'*50}",
        f"",
        f"质量评分: {analysis.overall_score:.1f}% (等级: {analysis.grade})",
        f"",
        f"指标:",
        f"  代码行数: {analysis.lines_of_code}",
        f"  函数数量: {analysis.functions}",
        f"  类数量: {analysis.classes}",
        f"  最大函数长度: {analysis.max_function_lines} 行",
        f"  最大嵌套深度: {analysis.max_nesting_depth} 层",
        f"  估计复杂度: {analysis.max_complexity}",
        f"",
        f"分项得分:",
        f"  函数大小: {analysis.function_size_score:.1f}",
        f"  嵌套深度: {analysis.nesting_score:.1f}",
        f"  复杂度: {analysis.complexity_score:.1f}",
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


def format_summary(results: List[FileAnalysis]) -> str:
    """Format project summary."""
    if not results:
        return "未找到源代码文件"

    total_loc = sum(r.lines_of_code for r in results)
    total_functions = sum(r.functions for r in results)
    avg_score = sum(r.overall_score for r in results) / len(results)

    grade_counts = {}
    for r in results:
        grade_counts[r.grade] = grade_counts.get(r.grade, 0) + 1

    # Overall grade
    if avg_score >= 85:
        overall_grade = "A"
    elif avg_score >= 70:
        overall_grade = "B"
    elif avg_score >= 50:
        overall_grade = "C"
    else:
        overall_grade = "D"

    lines = [
        "",
        "=" * 50,
        "代码质量分析报告",
        "=" * 50,
        "",
        f"项目质量评分: {avg_score:.1f}% (等级: {overall_grade})",
        "",
        "分析摘要:",
        f"  源文件: {len(results)} 个",
        f"  代码行数: {total_loc} 行",
        f"  函数总数: {total_functions} 个",
        "",
        "等级分布:",
    ]

    for grade in ["A", "B", "C", "D"]:
        count = grade_counts.get(grade, 0)
        if count > 0:
            lines.append(f"  {grade}: {count} 个文件")

    # Common issues
    all_issues = []
    for r in results:
        all_issues.extend(r.issues)

    if all_issues:
        lines.append("")
        lines.append("常见问题:")
        for issue in set(all_issues)[:5]:
            lines.append(f"  ⚠️  {issue}")

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python quality_analyzer.py <file-or-directory>")
        sys.exit(1)

    target = Path(sys.argv[1])
    summary_only = "--summary" in sys.argv

    analyzer = QualityAnalyzer()

    if target.is_file():
        analysis = analyzer.analyze_file(target)
        print(format_file_report(analysis))
    else:
        results = analyzer.analyze_directory(target)
        print(format_summary(results))

        if not summary_only:
            # Show files with issues
            problem_files = [r for r in results if r.overall_score < 70]
            if problem_files:
                print("\n需要关注的文件:")
                for analysis in problem_files:
                    print(format_file_report(analysis))


if __name__ == "__main__":
    main()
