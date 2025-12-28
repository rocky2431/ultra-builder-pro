#!/usr/bin/env python3
"""
Backend Security Audit Script

Scans backend code for common security vulnerabilities based on OWASP Top 10.
Supports JavaScript/TypeScript, Python, and Go codebases.

Usage:
    python security_audit.py <directory> [--severity <level>] [--format <format>]

Examples:
    python security_audit.py ./src
    python security_audit.py ./src --severity high
    python security_audit.py ./src --format json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Set


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """Security finding."""
    file: str
    line: int
    severity: Severity
    category: str
    title: str
    description: str
    recommendation: str
    code_snippet: Optional[str] = None


# ============================================================================
# Vulnerability Patterns
# ============================================================================

PATTERNS: Dict[str, List[dict]] = {
    # JavaScript/TypeScript patterns
    "js": [
        {
            "pattern": r"eval\s*\(",
            "severity": Severity.CRITICAL,
            "category": "Code Injection",
            "title": "Dangerous eval() usage",
            "description": "eval() can execute arbitrary code, leading to code injection vulnerabilities",
            "recommendation": "Use JSON.parse() for JSON, or safer alternatives like Function constructor with validation",
        },
        {
            "pattern": r"innerHTML\s*=",
            "severity": Severity.HIGH,
            "category": "XSS",
            "title": "Potential XSS via innerHTML",
            "description": "Setting innerHTML with user input can lead to Cross-Site Scripting",
            "recommendation": "Use textContent for text, or sanitize HTML with DOMPurify",
        },
        {
            "pattern": r"document\.write\s*\(",
            "severity": Severity.HIGH,
            "category": "XSS",
            "title": "Dangerous document.write()",
            "description": "document.write can introduce XSS vulnerabilities",
            "recommendation": "Use DOM manipulation methods instead",
        },
        {
            "pattern": r"new\s+Function\s*\(",
            "severity": Severity.HIGH,
            "category": "Code Injection",
            "title": "Dynamic Function creation",
            "description": "Creating functions dynamically can lead to code injection",
            "recommendation": "Avoid dynamic function creation, use static functions",
        },
        {
            "pattern": r"child_process\.exec\s*\(",
            "severity": Severity.CRITICAL,
            "category": "Command Injection",
            "title": "Potential command injection",
            "description": "exec() with user input can lead to command injection",
            "recommendation": "Use execFile() with arguments array, or validate/sanitize input",
        },
        {
            "pattern": r"(?:process\.env|dotenv).*(?:password|secret|key|token).*=.*['\"]",
            "severity": Severity.HIGH,
            "category": "Secrets Exposure",
            "title": "Hardcoded secret in code",
            "description": "Secrets should not be hardcoded in source code",
            "recommendation": "Use environment variables without default values in code",
        },
        {
            "pattern": r"jwt\.sign\s*\([^)]*['\"](?:secret|password|key)['\"]",
            "severity": Severity.CRITICAL,
            "category": "Weak Cryptography",
            "title": "Weak JWT secret",
            "description": "JWT signed with weak or hardcoded secret",
            "recommendation": "Use strong, randomly generated secrets from environment variables",
        },
        {
            "pattern": r"(?:md5|sha1)\s*\(",
            "severity": Severity.MEDIUM,
            "category": "Weak Cryptography",
            "title": "Weak hash algorithm",
            "description": "MD5 and SHA1 are cryptographically weak",
            "recommendation": "Use SHA-256 or stronger for hashing, bcrypt/argon2 for passwords",
        },
        {
            "pattern": r"(?:cors|CORS).*origin:\s*['\"]?\*['\"]?",
            "severity": Severity.MEDIUM,
            "category": "Security Misconfiguration",
            "title": "Permissive CORS configuration",
            "description": "Allowing all origins can expose API to cross-origin attacks",
            "recommendation": "Specify allowed origins explicitly",
        },
        {
            "pattern": r"(?:password|pwd)\s*[=:]\s*['\"][^'\"]+['\"]",
            "severity": Severity.CRITICAL,
            "category": "Secrets Exposure",
            "title": "Hardcoded password",
            "description": "Passwords should never be hardcoded",
            "recommendation": "Use environment variables or secure secret management",
        },
        {
            "pattern": r"\.query\s*\(\s*[`'\"].*\$\{",
            "severity": Severity.CRITICAL,
            "category": "SQL Injection",
            "title": "Potential SQL injection",
            "description": "String interpolation in SQL queries can lead to SQL injection",
            "recommendation": "Use parameterized queries or prepared statements",
        },
        {
            "pattern": r"res\.redirect\s*\(\s*req\.",
            "severity": Severity.HIGH,
            "category": "Open Redirect",
            "title": "Potential open redirect",
            "description": "Redirecting to user-supplied URLs can lead to phishing",
            "recommendation": "Validate redirect URLs against a whitelist",
        },
    ],

    # Python patterns
    "py": [
        {
            "pattern": r"eval\s*\(",
            "severity": Severity.CRITICAL,
            "category": "Code Injection",
            "title": "Dangerous eval() usage",
            "description": "eval() can execute arbitrary code",
            "recommendation": "Use ast.literal_eval() for parsing, or avoid eval entirely",
        },
        {
            "pattern": r"exec\s*\(",
            "severity": Severity.CRITICAL,
            "category": "Code Injection",
            "title": "Dangerous exec() usage",
            "description": "exec() can execute arbitrary code",
            "recommendation": "Avoid exec(), use safer alternatives",
        },
        {
            "pattern": r"subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True",
            "severity": Severity.CRITICAL,
            "category": "Command Injection",
            "title": "Shell injection risk",
            "description": "shell=True with user input can lead to command injection",
            "recommendation": "Use shell=False with arguments as a list",
        },
        {
            "pattern": r"os\.system\s*\(",
            "severity": Severity.HIGH,
            "category": "Command Injection",
            "title": "Potential command injection",
            "description": "os.system() is vulnerable to command injection",
            "recommendation": "Use subprocess with shell=False",
        },
        {
            "pattern": r"pickle\.(?:load|loads)\s*\(",
            "severity": Severity.HIGH,
            "category": "Deserialization",
            "title": "Unsafe deserialization",
            "description": "Pickle can execute arbitrary code during deserialization",
            "recommendation": "Use JSON or other safe formats for untrusted data",
        },
        {
            "pattern": r"yaml\.load\s*\([^)]*Loader\s*=\s*None",
            "severity": Severity.HIGH,
            "category": "Deserialization",
            "title": "Unsafe YAML loading",
            "description": "YAML load without SafeLoader can execute arbitrary code",
            "recommendation": "Use yaml.safe_load() or Loader=yaml.SafeLoader",
        },
        {
            "pattern": r"(?:execute|raw)\s*\([^)]*%s",
            "severity": Severity.CRITICAL,
            "category": "SQL Injection",
            "title": "Potential SQL injection",
            "description": "String formatting in SQL can lead to injection",
            "recommendation": "Use parameterized queries with %s as placeholder",
        },
        {
            "pattern": r"f['\"].*(?:SELECT|INSERT|UPDATE|DELETE).*\{",
            "severity": Severity.CRITICAL,
            "category": "SQL Injection",
            "title": "SQL injection via f-string",
            "description": "F-string interpolation in SQL queries is dangerous",
            "recommendation": "Use parameterized queries",
        },
        {
            "pattern": r"(?:password|secret|api_key)\s*=\s*['\"][^'\"]+['\"]",
            "severity": Severity.HIGH,
            "category": "Secrets Exposure",
            "title": "Hardcoded secret",
            "description": "Secrets should not be hardcoded",
            "recommendation": "Use environment variables via os.getenv()",
        },
        {
            "pattern": r"(?:md5|sha1)\s*\(",
            "severity": Severity.MEDIUM,
            "category": "Weak Cryptography",
            "title": "Weak hash algorithm",
            "description": "MD5 and SHA1 are cryptographically weak",
            "recommendation": "Use hashlib.sha256() or stronger",
        },
        {
            "pattern": r"verify\s*=\s*False",
            "severity": Severity.HIGH,
            "category": "Security Misconfiguration",
            "title": "SSL verification disabled",
            "description": "Disabling SSL verification exposes to MITM attacks",
            "recommendation": "Keep verify=True, fix certificate issues properly",
        },
        {
            "pattern": r"DEBUG\s*=\s*True",
            "severity": Severity.MEDIUM,
            "category": "Security Misconfiguration",
            "title": "Debug mode enabled",
            "description": "Debug mode can expose sensitive information",
            "recommendation": "Disable debug mode in production",
        },
    ],

    # Go patterns
    "go": [
        {
            "pattern": r"fmt\.Sprintf\s*\([^)]*(?:SELECT|INSERT|UPDATE|DELETE)",
            "severity": Severity.CRITICAL,
            "category": "SQL Injection",
            "title": "Potential SQL injection",
            "description": "String formatting in SQL can lead to injection",
            "recommendation": "Use parameterized queries with database/sql",
        },
        {
            "pattern": r"exec\.Command\s*\([^)]*\+",
            "severity": Severity.HIGH,
            "category": "Command Injection",
            "title": "Potential command injection",
            "description": "String concatenation in commands is dangerous",
            "recommendation": "Use separate arguments, validate input",
        },
        {
            "pattern": r"http\.ListenAndServe\s*\([^)]*['\"]:[0-9]+['\"]",
            "severity": Severity.MEDIUM,
            "category": "Security Misconfiguration",
            "title": "HTTP without TLS",
            "description": "Serving HTTP without TLS exposes data in transit",
            "recommendation": "Use http.ListenAndServeTLS() in production",
        },
        {
            "pattern": r"InsecureSkipVerify\s*:\s*true",
            "severity": Severity.HIGH,
            "category": "Security Misconfiguration",
            "title": "TLS verification disabled",
            "description": "Skipping TLS verification exposes to MITM attacks",
            "recommendation": "Keep InsecureSkipVerify: false",
        },
        {
            "pattern": r"(?:password|secret|apiKey)\s*:?=\s*\"[^\"]+\"",
            "severity": Severity.HIGH,
            "category": "Secrets Exposure",
            "title": "Hardcoded secret",
            "description": "Secrets should not be hardcoded",
            "recommendation": "Use environment variables via os.Getenv()",
        },
        {
            "pattern": r"md5\.(?:New|Sum)",
            "severity": Severity.MEDIUM,
            "category": "Weak Cryptography",
            "title": "Weak hash algorithm (MD5)",
            "description": "MD5 is cryptographically broken",
            "recommendation": "Use sha256 from crypto/sha256",
        },
        {
            "pattern": r"sha1\.(?:New|Sum)",
            "severity": Severity.MEDIUM,
            "category": "Weak Cryptography",
            "title": "Weak hash algorithm (SHA1)",
            "description": "SHA1 is cryptographically weak",
            "recommendation": "Use sha256 from crypto/sha256",
        },
        {
            "pattern": r"template\.HTML\s*\(",
            "severity": Severity.MEDIUM,
            "category": "XSS",
            "title": "Unescaped HTML in template",
            "description": "template.HTML bypasses auto-escaping",
            "recommendation": "Ensure input is sanitized before using template.HTML",
        },
    ],
}

# File extension to pattern group mapping
EXTENSION_MAP = {
    ".js": "js",
    ".ts": "js",
    ".jsx": "js",
    ".tsx": "js",
    ".mjs": "js",
    ".cjs": "js",
    ".py": "py",
    ".go": "go",
}


# ============================================================================
# Scanner
# ============================================================================

class SecurityScanner:
    """Scans code for security vulnerabilities."""

    def __init__(self, min_severity: Severity = Severity.INFO):
        self.min_severity = min_severity
        self.severity_order = [
            Severity.INFO,
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
            Severity.CRITICAL,
        ]

    def should_report(self, severity: Severity) -> bool:
        """Check if severity meets minimum threshold."""
        return self.severity_order.index(severity) >= self.severity_order.index(self.min_severity)

    def scan_file(self, file_path: Path) -> List[Finding]:
        """Scan a single file for vulnerabilities."""
        findings = []

        ext = file_path.suffix.lower()
        if ext not in EXTENSION_MAP:
            return findings

        pattern_group = EXTENSION_MAP[ext]
        patterns = PATTERNS.get(pattern_group, [])

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
        except Exception:
            return findings

        for pattern_def in patterns:
            pattern = re.compile(pattern_def["pattern"], re.IGNORECASE)

            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    severity = pattern_def["severity"]
                    if self.should_report(severity):
                        findings.append(Finding(
                            file=str(file_path),
                            line=line_num,
                            severity=severity,
                            category=pattern_def["category"],
                            title=pattern_def["title"],
                            description=pattern_def["description"],
                            recommendation=pattern_def["recommendation"],
                            code_snippet=line.strip()[:100],
                        ))

        return findings

    def scan_directory(self, directory: Path) -> List[Finding]:
        """Scan a directory recursively for vulnerabilities."""
        findings = []

        # Directories to skip
        skip_dirs = {
            "node_modules", "vendor", "venv", ".venv", "__pycache__",
            ".git", ".svn", "dist", "build", ".next", "coverage",
        }

        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                file_path = Path(root) / file
                findings.extend(self.scan_file(file_path))

        # Sort by severity (critical first)
        findings.sort(
            key=lambda f: self.severity_order.index(f.severity),
            reverse=True
        )

        return findings


# ============================================================================
# Reporters
# ============================================================================

def report_text(findings: List[Finding]) -> str:
    """Generate text report."""
    if not findings:
        return "✅ No security issues found!"

    lines = [
        "=" * 70,
        "SECURITY AUDIT REPORT",
        "=" * 70,
        "",
    ]

    # Summary
    severity_counts = {}
    for f in findings:
        severity_counts[f.severity.value] = severity_counts.get(f.severity.value, 0) + 1

    lines.append("SUMMARY:")
    for sev in ["critical", "high", "medium", "low", "info"]:
        if sev in severity_counts:
            lines.append(f"  {sev.upper()}: {severity_counts[sev]}")
    lines.append("")

    # Group by category
    by_category: Dict[str, List[Finding]] = {}
    for f in findings:
        by_category.setdefault(f.category, []).append(f)

    for category, cat_findings in sorted(by_category.items()):
        lines.append("-" * 70)
        lines.append(f"[{category}]")
        lines.append("-" * 70)

        for f in cat_findings:
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
                "info": "⚪",
            }.get(f.severity.value, "⚪")

            lines.append("")
            lines.append(f"{severity_icon} [{f.severity.value.upper()}] {f.title}")
            lines.append(f"   File: {f.file}:{f.line}")
            lines.append(f"   {f.description}")
            if f.code_snippet:
                lines.append(f"   Code: {f.code_snippet}")
            lines.append(f"   Fix: {f.recommendation}")

    lines.append("")
    lines.append("=" * 70)
    lines.append(f"Total: {len(findings)} issue(s) found")
    lines.append("=" * 70)

    return "\n".join(lines)


def report_json(findings: List[Finding]) -> str:
    """Generate JSON report."""
    return json.dumps(
        {
            "total": len(findings),
            "findings": [
                {**asdict(f), "severity": f.severity.value}
                for f in findings
            ],
        },
        indent=2,
    )


def report_sarif(findings: List[Finding]) -> str:
    """Generate SARIF report for GitHub integration."""
    rules = {}
    results = []

    for f in findings:
        rule_id = f"{f.category.replace(' ', '_')}_{f.title.replace(' ', '_')}"

        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": f.title,
                "shortDescription": {"text": f.title},
                "fullDescription": {"text": f.description},
                "help": {"text": f.recommendation},
                "defaultConfiguration": {
                    "level": {
                        "critical": "error",
                        "high": "error",
                        "medium": "warning",
                        "low": "note",
                        "info": "note",
                    }.get(f.severity.value, "warning")
                },
            }

        results.append({
            "ruleId": rule_id,
            "level": rules[rule_id]["defaultConfiguration"]["level"],
            "message": {"text": f"{f.description}. {f.recommendation}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.file},
                    "region": {"startLine": f.line},
                }
            }],
        })

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "security-audit",
                    "version": "1.0.0",
                    "rules": list(rules.values()),
                }
            },
            "results": results,
        }],
    }

    return json.dumps(sarif, indent=2)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Scan backend code for security vulnerabilities"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory to scan",
    )
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low", "info"],
        default="low",
        help="Minimum severity to report (default: low)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code if issues found",
    )

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)

    min_severity = Severity(args.severity)
    scanner = SecurityScanner(min_severity=min_severity)
    findings = scanner.scan_directory(args.directory)

    if args.format == "json":
        print(report_json(findings))
    elif args.format == "sarif":
        print(report_sarif(findings))
    else:
        print(report_text(findings))

    if args.exit_code and findings:
        # Exit with number of critical/high issues (max 125)
        critical_high = sum(
            1 for f in findings
            if f.severity in [Severity.CRITICAL, Severity.HIGH]
        )
        sys.exit(min(critical_high, 125) or 1)


if __name__ == "__main__":
    main()
