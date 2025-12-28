#!/usr/bin/env python3
"""
SQL Analyzer Script

Analyzes SQL queries and schema for optimization opportunities.
Supports PostgreSQL, MySQL, and SQLite.

Usage:
    python sql_analyzer.py <file_or_directory> [--format <format>]

Examples:
    python sql_analyzer.py ./migrations
    python sql_analyzer.py query.sql --format json
    python sql_analyzer.py ./src --pattern "*.sql"
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple


class IssueType(Enum):
    PERFORMANCE = "performance"
    DESIGN = "design"
    SECURITY = "security"
    BEST_PRACTICE = "best_practice"


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Issue:
    """SQL analysis issue."""
    file: str
    line: int
    issue_type: IssueType
    severity: Severity
    title: str
    description: str
    suggestion: str
    sql_snippet: Optional[str] = None


@dataclass
class IndexSuggestion:
    """Index optimization suggestion."""
    table: str
    columns: List[str]
    reason: str
    impact: str


# ============================================================================
# SQL Patterns
# ============================================================================

SQL_PATTERNS = [
    # Performance issues
    {
        "pattern": r"SELECT\s+\*\s+FROM",
        "type": IssueType.PERFORMANCE,
        "severity": Severity.MEDIUM,
        "title": "SELECT * usage",
        "description": "SELECT * fetches all columns, which can be inefficient",
        "suggestion": "Specify only needed columns explicitly",
    },
    {
        "pattern": r"SELECT.*FROM.*(?:WHERE|AND|OR)\s+\w+\s+LIKE\s+['\"]%",
        "type": IssueType.PERFORMANCE,
        "severity": Severity.HIGH,
        "title": "Leading wildcard in LIKE",
        "description": "Leading wildcard (LIKE '%...') prevents index usage",
        "suggestion": "Consider full-text search or redesign query to use trailing wildcard",
    },
    {
        "pattern": r"(?:WHERE|AND|OR)\s+(?:UPPER|LOWER|TRIM|SUBSTRING)\s*\(",
        "type": IssueType.PERFORMANCE,
        "severity": Severity.MEDIUM,
        "title": "Function on indexed column",
        "description": "Applying functions to columns in WHERE prevents index usage",
        "suggestion": "Create functional index or normalize data in application",
    },
    {
        "pattern": r"SELECT.*FROM.*(?:WHERE|AND|OR)\s+NOT\s+IN\s*\(",
        "type": IssueType.PERFORMANCE,
        "severity": Severity.MEDIUM,
        "title": "NOT IN with subquery",
        "description": "NOT IN with subquery can be slow and has NULL handling issues",
        "suggestion": "Use NOT EXISTS or LEFT JOIN ... IS NULL instead",
    },
    {
        "pattern": r"ORDER\s+BY\s+\d+",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.LOW,
        "title": "ORDER BY column number",
        "description": "Ordering by column position is fragile and unclear",
        "suggestion": "Use explicit column names in ORDER BY",
    },
    {
        "pattern": r"LIMIT\s+\d+\s+OFFSET\s+\d{4,}",
        "type": IssueType.PERFORMANCE,
        "severity": Severity.HIGH,
        "title": "Large OFFSET pagination",
        "description": "Large OFFSET values cause performance issues",
        "suggestion": "Use keyset pagination (WHERE id > last_id) instead",
    },
    {
        "pattern": r"SELECT\s+DISTINCT",
        "type": IssueType.PERFORMANCE,
        "severity": Severity.LOW,
        "title": "DISTINCT usage",
        "description": "DISTINCT can indicate design issues or be performance-heavy",
        "suggestion": "Review if DISTINCT is necessary, consider GROUP BY or fixing duplicates",
    },
    {
        "pattern": r"(?:WHERE|AND|OR)\s+1\s*=\s*1",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.LOW,
        "title": "Tautology in WHERE clause",
        "description": "1=1 is often used for dynamic query building but adds noise",
        "suggestion": "Build queries dynamically without tautologies",
    },

    # Schema design issues
    {
        "pattern": r"CREATE\s+TABLE.*\(\s*id\s+INT(?:EGER)?\s+",
        "type": IssueType.DESIGN,
        "severity": Severity.MEDIUM,
        "title": "Using INT for primary key",
        "description": "INT may overflow for large tables",
        "suggestion": "Consider BIGINT or UUID for primary keys",
    },
    {
        "pattern": r"VARCHAR\s*\(\s*(?:255|256)\s*\)",
        "type": IssueType.DESIGN,
        "severity": Severity.INFO,
        "title": "Magic number VARCHAR(255)",
        "description": "255/256 is often arbitrary, not based on business requirements",
        "suggestion": "Choose VARCHAR length based on actual data requirements",
    },
    {
        "pattern": r"FLOAT|DOUBLE",
        "type": IssueType.DESIGN,
        "severity": Severity.MEDIUM,
        "title": "Floating point for precision data",
        "description": "FLOAT/DOUBLE have precision issues for monetary values",
        "suggestion": "Use DECIMAL/NUMERIC for money and other precision-critical data",
    },
    {
        "pattern": r"CREATE\s+TABLE(?:(?!REFERENCES).)*\)",
        "type": IssueType.DESIGN,
        "severity": Severity.INFO,
        "title": "Table without foreign keys",
        "description": "Tables without foreign keys may lack referential integrity",
        "suggestion": "Consider adding foreign key constraints for related tables",
    },
    {
        "pattern": r"(?:created|updated|deleted)_at\s+(?:TIMESTAMP|DATETIME)(?!\s+(?:DEFAULT|WITH))",
        "type": IssueType.DESIGN,
        "severity": Severity.LOW,
        "title": "Timestamp without default",
        "description": "Timestamp columns should have defaults for consistency",
        "suggestion": "Add DEFAULT NOW() or DEFAULT CURRENT_TIMESTAMP",
    },
    {
        "pattern": r"TEXT\s+NOT\s+NULL",
        "type": IssueType.DESIGN,
        "severity": Severity.INFO,
        "title": "TEXT column as NOT NULL",
        "description": "NOT NULL TEXT without default may cause insert issues",
        "suggestion": "Add DEFAULT '' or consider if NULL is acceptable",
    },

    # Security issues
    {
        "pattern": r"--.*password|password.*--",
        "type": IssueType.SECURITY,
        "severity": Severity.HIGH,
        "title": "Password in SQL comment",
        "description": "Passwords should never appear in SQL files",
        "suggestion": "Remove password from comments, use secure credential management",
    },
    {
        "pattern": r"GRANT\s+ALL\s+(?:PRIVILEGES\s+)?ON",
        "type": IssueType.SECURITY,
        "severity": Severity.MEDIUM,
        "title": "Overly permissive GRANT",
        "description": "GRANT ALL gives more permissions than typically needed",
        "suggestion": "Grant only required permissions (SELECT, INSERT, UPDATE, DELETE)",
    },
    {
        "pattern": r"CREATE\s+USER.*IDENTIFIED\s+BY\s+['\"][^'\"]+['\"]",
        "type": IssueType.SECURITY,
        "severity": Severity.HIGH,
        "title": "Hardcoded password in SQL",
        "description": "Passwords should not be hardcoded in SQL files",
        "suggestion": "Use environment variables or secret management",
    },

    # Best practices
    {
        "pattern": r"DROP\s+TABLE(?!\s+IF\s+EXISTS)",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.LOW,
        "title": "DROP TABLE without IF EXISTS",
        "description": "DROP without IF EXISTS may cause errors",
        "suggestion": "Use DROP TABLE IF EXISTS for idempotent migrations",
    },
    {
        "pattern": r"ALTER\s+TABLE.*ADD.*(?:COLUMN)?(?!.*(?:DEFAULT|NULL))",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.MEDIUM,
        "title": "Adding column without NULL/DEFAULT",
        "description": "Adding NOT NULL column without default blocks on existing rows",
        "suggestion": "Add column as NULL, backfill data, then add NOT NULL constraint",
    },
    {
        "pattern": r"CREATE\s+INDEX(?!\s+CONCURRENTLY)",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.INFO,
        "title": "Non-concurrent index creation",
        "description": "CREATE INDEX locks the table during creation",
        "suggestion": "Use CREATE INDEX CONCURRENTLY for production (PostgreSQL)",
    },
    {
        "pattern": r"DELETE\s+FROM\s+\w+(?!\s+WHERE)",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.HIGH,
        "title": "DELETE without WHERE clause",
        "description": "DELETE without WHERE removes all rows",
        "suggestion": "Add WHERE clause or use TRUNCATE if intentional",
    },
    {
        "pattern": r"UPDATE\s+\w+\s+SET(?!\s+.*WHERE)",
        "type": IssueType.BEST_PRACTICE,
        "severity": Severity.HIGH,
        "title": "UPDATE without WHERE clause",
        "description": "UPDATE without WHERE affects all rows",
        "suggestion": "Add WHERE clause to limit affected rows",
    },
]


# ============================================================================
# Analyzer
# ============================================================================

class SQLAnalyzer:
    """Analyzes SQL for issues and optimization opportunities."""

    def __init__(self):
        self.compiled_patterns = [
            (re.compile(p["pattern"], re.IGNORECASE | re.MULTILINE), p)
            for p in SQL_PATTERNS
        ]

    def analyze_file(self, file_path: Path) -> List[Issue]:
        """Analyze a single SQL file."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return issues

        lines = content.split("\n")

        for regex, pattern_def in self.compiled_patterns:
            for match in regex.finditer(content):
                # Calculate line number
                line_num = content[:match.start()].count("\n") + 1
                snippet = lines[line_num - 1].strip()[:100] if line_num <= len(lines) else ""

                issues.append(Issue(
                    file=str(file_path),
                    line=line_num,
                    issue_type=pattern_def["type"],
                    severity=pattern_def["severity"],
                    title=pattern_def["title"],
                    description=pattern_def["description"],
                    suggestion=pattern_def["suggestion"],
                    sql_snippet=snippet,
                ))

        # Additional analysis
        issues.extend(self._analyze_missing_indexes(file_path, content))

        return issues

    def _analyze_missing_indexes(self, file_path: Path, content: str) -> List[Issue]:
        """Analyze for potentially missing indexes."""
        issues = []

        # Find WHERE/JOIN clauses and suggest indexes
        where_pattern = re.compile(
            r"(?:WHERE|JOIN.*ON)\s+(\w+)\.(\w+)\s*[=<>]",
            re.IGNORECASE
        )

        # Track suggested indexes to avoid duplicates
        suggested: Set[Tuple[str, str]] = set()

        for match in where_pattern.finditer(content):
            table, column = match.groups()
            key = (table.lower(), column.lower())

            if key not in suggested:
                suggested.add(key)
                line_num = content[:match.start()].count("\n") + 1

                issues.append(Issue(
                    file=str(file_path),
                    line=line_num,
                    issue_type=IssueType.PERFORMANCE,
                    severity=Severity.INFO,
                    title=f"Potential index candidate: {table}.{column}",
                    description=f"Column {column} is used in WHERE/JOIN, may benefit from indexing",
                    suggestion=f"Consider: CREATE INDEX ix_{table}_{column} ON {table}({column})",
                    sql_snippet=None,
                ))

        return issues

    def analyze_directory(self, directory: Path, pattern: str = "*.sql") -> List[Issue]:
        """Analyze all SQL files in a directory."""
        issues = []

        for sql_file in directory.rglob(pattern):
            if any(skip in str(sql_file) for skip in [
                "node_modules", "vendor", ".git", "__pycache__"
            ]):
                continue
            issues.extend(self.analyze_file(sql_file))

        # Sort by severity
        severity_order = [Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
        issues.sort(key=lambda i: severity_order.index(i.severity))

        return issues

    def suggest_indexes(self, content: str) -> List[IndexSuggestion]:
        """Analyze SQL and suggest indexes."""
        suggestions = []

        # Extract table and column usage from queries
        select_pattern = re.compile(
            r"SELECT.*?FROM\s+(\w+).*?WHERE\s+(.*?)(?:ORDER BY|GROUP BY|LIMIT|$)",
            re.IGNORECASE | re.DOTALL
        )

        for match in select_pattern.finditer(content):
            table = match.group(1)
            where_clause = match.group(2)

            # Find columns in WHERE
            columns = re.findall(r"(\w+)\s*[=<>!]", where_clause)
            if columns:
                suggestions.append(IndexSuggestion(
                    table=table,
                    columns=list(set(columns)),
                    reason="Columns used in WHERE clause",
                    impact="May improve query performance significantly",
                ))

        return suggestions


# ============================================================================
# Reporters
# ============================================================================

def report_text(issues: List[Issue]) -> str:
    """Generate text report."""
    if not issues:
        return "✅ No SQL issues found!"

    lines = [
        "=" * 70,
        "SQL ANALYSIS REPORT",
        "=" * 70,
        "",
    ]

    # Summary
    by_severity = {}
    for issue in issues:
        by_severity[issue.severity.value] = by_severity.get(issue.severity.value, 0) + 1

    lines.append("SUMMARY:")
    for sev in ["high", "medium", "low", "info"]:
        if sev in by_severity:
            lines.append(f"  {sev.upper()}: {by_severity[sev]}")
    lines.append("")

    # Group by type
    by_type: Dict[str, List[Issue]] = {}
    for issue in issues:
        by_type.setdefault(issue.issue_type.value, []).append(issue)

    type_labels = {
        "performance": "⚡ Performance Issues",
        "design": "📐 Design Issues",
        "security": "🔒 Security Issues",
        "best_practice": "📋 Best Practice Issues",
    }

    for issue_type, type_issues in sorted(by_type.items()):
        lines.append("-" * 70)
        lines.append(type_labels.get(issue_type, issue_type.upper()))
        lines.append("-" * 70)

        for issue in type_issues:
            severity_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🔵",
                "info": "⚪",
            }.get(issue.severity.value, "⚪")

            lines.append("")
            lines.append(f"{severity_icon} [{issue.severity.value.upper()}] {issue.title}")
            lines.append(f"   File: {issue.file}:{issue.line}")
            lines.append(f"   {issue.description}")
            if issue.sql_snippet:
                lines.append(f"   SQL: {issue.sql_snippet}")
            lines.append(f"   Fix: {issue.suggestion}")

    lines.append("")
    lines.append("=" * 70)
    lines.append(f"Total: {len(issues)} issue(s) found")
    lines.append("=" * 70)

    return "\n".join(lines)


def report_json(issues: List[Issue]) -> str:
    """Generate JSON report."""
    return json.dumps(
        {
            "total": len(issues),
            "issues": [
                {
                    **asdict(issue),
                    "issue_type": issue.issue_type.value,
                    "severity": issue.severity.value,
                }
                for issue in issues
            ],
        },
        indent=2,
    )


def report_markdown(issues: List[Issue]) -> str:
    """Generate Markdown report."""
    if not issues:
        return "# SQL Analysis Report\n\n✅ No issues found!"

    lines = [
        "# SQL Analysis Report",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]

    by_severity = {}
    for issue in issues:
        by_severity[issue.severity.value] = by_severity.get(issue.severity.value, 0) + 1

    for sev in ["high", "medium", "low", "info"]:
        if sev in by_severity:
            lines.append(f"| {sev.upper()} | {by_severity[sev]} |")

    lines.append("")
    lines.append("## Issues")
    lines.append("")

    for issue in issues:
        emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🔵",
            "info": "⚪",
        }.get(issue.severity.value, "")

        lines.append(f"### {emoji} {issue.title}")
        lines.append("")
        lines.append(f"**File:** `{issue.file}:{issue.line}`")
        lines.append(f"**Severity:** {issue.severity.value.upper()}")
        lines.append(f"**Type:** {issue.issue_type.value}")
        lines.append("")
        lines.append(issue.description)
        lines.append("")
        if issue.sql_snippet:
            lines.append("```sql")
            lines.append(issue.sql_snippet)
            lines.append("```")
            lines.append("")
        lines.append(f"**Suggestion:** {issue.suggestion}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze SQL files for issues and optimization opportunities"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to analyze",
    )
    parser.add_argument(
        "--pattern",
        default="*.sql",
        help="File pattern for directory scan (default: *.sql)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code if issues found",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    analyzer = SQLAnalyzer()

    if args.path.is_file():
        issues = analyzer.analyze_file(args.path)
    else:
        issues = analyzer.analyze_directory(args.path, args.pattern)

    if args.format == "json":
        print(report_json(issues))
    elif args.format == "markdown":
        print(report_markdown(issues))
    else:
        print(report_text(issues))

    if args.exit_code and issues:
        high_medium = sum(
            1 for i in issues
            if i.severity in [Severity.HIGH, Severity.MEDIUM]
        )
        sys.exit(min(high_medium, 125) or 1)


if __name__ == "__main__":
    main()
