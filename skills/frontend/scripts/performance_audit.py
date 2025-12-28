#!/usr/bin/env python3
"""
Frontend Performance Audit Script

Analyzes frontend components for common performance issues.

Usage:
    python performance_audit.py <file-or-directory>
    python performance_audit.py src/components/
    python performance_audit.py src/components/Button.tsx
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Severity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Issue:
    severity: Severity
    category: str
    message: str
    file: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


class PerformanceAuditor:
    """Analyzes frontend code for performance issues."""

    # React performance patterns
    REACT_PATTERNS = [
        # Inline object/array props
        (
            r'<\w+[^>]*\s(style|className)=\{[^}]*\{[^}]+\}[^}]*\}',
            Severity.MEDIUM,
            "Inline object in JSX props",
            "Move to useMemo or define outside component",
        ),
        # Missing useCallback for handlers
        (
            r'on\w+=\{\s*\([^)]*\)\s*=>\s*\{',
            Severity.LOW,
            "Inline arrow function in event handler",
            "Consider useCallback for stable reference",
        ),
        # Array.map without key
        (
            r'\.map\([^)]+\)\s*=>\s*[^{]*<[^>]+(?!key=)',
            Severity.HIGH,
            "Possible missing key in map",
            "Add unique key prop to mapped elements",
        ),
        # useEffect with empty deps but using state
        (
            r'useEffect\(\s*\(\)\s*=>\s*\{[^}]*set\w+[^}]*\}\s*,\s*\[\s*\]\s*\)',
            Severity.MEDIUM,
            "useEffect with empty deps may have stale closure",
            "Review dependencies or use functional update",
        ),
        # Large component without memo
        (
            r'export\s+(?:default\s+)?function\s+\w+',
            Severity.LOW,
            "Component may benefit from React.memo",
            "Consider memo() for expensive components",
        ),
    ]

    # Vue performance patterns
    VUE_PATTERNS = [
        # Deep watcher on large objects
        (
            r'watch\([^,]+,\s*[^,]+,\s*\{[^}]*deep:\s*true',
            Severity.MEDIUM,
            "Deep watcher may cause performance issues",
            "Use shallowRef or watch specific paths",
        ),
        # v-if with v-for
        (
            r'v-for=[^>]+v-if=|v-if=[^>]+v-for=',
            Severity.HIGH,
            "v-if used with v-for on same element",
            "Move v-if to wrapper element or use computed",
        ),
        # Missing key in v-for
        (
            r'v-for="[^"]+"\s*(?!:key|v-bind:key)',
            Severity.HIGH,
            "Missing :key in v-for",
            "Add unique :key binding",
        ),
    ]

    # General performance patterns
    GENERAL_PATTERNS = [
        # Large bundle imports
        (
            r'import\s+\*\s+as\s+\w+\s+from\s+[\'"](?:lodash|moment|date-fns)[\'"]',
            Severity.HIGH,
            "Importing entire library",
            "Use named imports for tree shaking",
        ),
        # Synchronous require
        (
            r'require\([\'"][^\'"]+[\'"]\)',
            Severity.LOW,
            "Synchronous require",
            "Use dynamic import() for code splitting",
        ),
        # Console.log in production
        (
            r'console\.(log|debug|info)\(',
            Severity.LOW,
            "Console statement found",
            "Remove or use conditional logging",
        ),
        # Inline styles
        (
            r'style=\{?\{[^}]+\}',
            Severity.LOW,
            "Inline styles may prevent optimization",
            "Consider CSS modules or styled-components",
        ),
    ]

    # Image optimization patterns
    IMAGE_PATTERNS = [
        # img without dimensions
        (
            r'<img[^>]+src=[^>]+(?!width=|height=|style=)',
            Severity.MEDIUM,
            "Image without explicit dimensions (may cause CLS)",
            "Add width and height attributes",
        ),
        # img without lazy loading
        (
            r'<img[^>]+(?!loading=)',
            Severity.LOW,
            "Image without lazy loading",
            "Add loading=\"lazy\" for below-fold images",
        ),
        # Using img instead of next/image
        (
            r'<img\s+src=',
            Severity.LOW,
            "Using native img instead of optimized component",
            "Use next/image or responsive images",
        ),
    ]

    def __init__(self):
        self.issues: List[Issue] = []

    def audit_file(self, file_path: Path) -> List[Issue]:
        """Audit a single file for performance issues."""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Determine file type
            suffix = file_path.suffix.lower()
            is_react = suffix in ['.tsx', '.jsx'] or 'react' in content.lower()
            is_vue = suffix == '.vue'

            # Apply patterns based on file type
            patterns = self.GENERAL_PATTERNS + self.IMAGE_PATTERNS

            if is_react:
                patterns += self.REACT_PATTERNS
            if is_vue:
                patterns += self.VUE_PATTERNS

            for pattern, severity, message, suggestion in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(Issue(
                            severity=severity,
                            category="Performance",
                            message=message,
                            file=str(file_path),
                            line=i,
                            suggestion=suggestion,
                        ))

            # Check file size
            if len(content) > 500 * 80:  # ~500 lines
                issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="Maintainability",
                    message=f"Large file ({len(lines)} lines)",
                    file=str(file_path),
                    suggestion="Consider splitting into smaller components",
                ))

        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

        return issues

    def audit_directory(self, dir_path: Path) -> List[Issue]:
        """Audit all frontend files in a directory."""
        issues = []
        extensions = ['.tsx', '.jsx', '.ts', '.js', '.vue']

        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                # Skip node_modules and build directories
                if 'node_modules' in str(file_path) or 'dist' in str(file_path):
                    continue
                issues.extend(self.audit_file(file_path))

        return issues

    def audit(self, path: str) -> List[Issue]:
        """Audit file or directory."""
        target = Path(path)

        if target.is_file():
            return self.audit_file(target)
        elif target.is_dir():
            return self.audit_directory(target)
        else:
            print(f"Error: {path} not found", file=sys.stderr)
            return []


def format_report(issues: List[Issue]) -> str:
    """Format audit results."""
    if not issues:
        return "\n✅ No performance issues found!\n"

    # Group by severity
    high = [i for i in issues if i.severity == Severity.HIGH]
    medium = [i for i in issues if i.severity == Severity.MEDIUM]
    low = [i for i in issues if i.severity == Severity.LOW]

    lines = [
        "",
        "=" * 60,
        "前端性能审计报告 (Frontend Performance Audit)",
        "=" * 60,
        "",
        f"发现问题: {len(issues)} 个",
        f"  🔴 高优先级: {len(high)}",
        f"  🟡 中优先级: {len(medium)}",
        f"  🟢 低优先级: {len(low)}",
        "",
    ]

    def format_issues(issues: List[Issue], icon: str) -> List[str]:
        result = []
        for issue in issues:
            result.append(f"{icon} [{issue.category}] {issue.message}")
            result.append(f"   文件: {issue.file}" + (f":{issue.line}" if issue.line else ""))
            if issue.suggestion:
                result.append(f"   建议: {issue.suggestion}")
            result.append("")
        return result

    if high:
        lines.append("-" * 60)
        lines.append("🔴 高优先级问题:")
        lines.append("-" * 60)
        lines.extend(format_issues(high, "🔴"))

    if medium:
        lines.append("-" * 60)
        lines.append("🟡 中优先级问题:")
        lines.append("-" * 60)
        lines.extend(format_issues(medium, "🟡"))

    if low:
        lines.append("-" * 60)
        lines.append("🟢 低优先级问题:")
        lines.append("-" * 60)
        lines.extend(format_issues(low, "🟢"))

    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python performance_audit.py <file-or-directory>")
        print("Example: python performance_audit.py src/components/")
        sys.exit(1)

    target = sys.argv[1]
    auditor = PerformanceAuditor()
    issues = auditor.audit(target)

    print(format_report(issues))

    # Exit with error code if high-severity issues found
    high_issues = [i for i in issues if i.severity == Severity.HIGH]
    if high_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
