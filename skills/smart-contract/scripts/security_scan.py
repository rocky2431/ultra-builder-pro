#!/usr/bin/env python3
"""
Smart Contract Security Scanner

Performs static analysis to detect common vulnerability patterns.
This is a lightweight scanner - for production audits, use Slither, Mythril, etc.

Usage:
    python security_scan.py <contract.sol>
    python security_scan.py <directory>
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Finding:
    severity: Severity
    title: str
    description: str
    line: int
    code: str
    recommendation: str


class SecurityScanner:
    def __init__(self):
        self.findings: List[Finding] = []

    def scan_file(self, filepath: Path) -> List[Finding]:
        """Scan a single Solidity file for vulnerabilities."""
        self.findings = []
        content = filepath.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            self._check_reentrancy(line, i, lines)
            self._check_tx_origin(line, i)
            self._check_unchecked_call(line, i)
            self._check_floating_pragma(line, i)
            self._check_deprecated_functions(line, i)
            self._check_hardcoded_addresses(line, i)
            self._check_assembly(line, i)
            self._check_selfdestruct(line, i)
            self._check_delegatecall(line, i)
            self._check_block_timestamp(line, i)

        # Multi-line checks
        self._check_missing_reentrancy_guard(content, lines)
        self._check_external_calls_in_loop(content, lines)

        return self.findings

    def _check_reentrancy(self, line: str, line_num: int, lines: List[str]):
        """Detect potential reentrancy vulnerabilities."""
        # Pattern: external call followed by state change
        call_patterns = [
            r'\.call\{',
            r'\.call\(',
            r'\.transfer\(',
            r'\.send\(',
        ]

        for pattern in call_patterns:
            if re.search(pattern, line):
                # Check if there are state changes after this line
                for j in range(line_num, min(line_num + 10, len(lines))):
                    subsequent_line = lines[j - 1] if j <= len(lines) else ""
                    if re.search(r'\w+\s*[+\-*/]?=\s*', subsequent_line):
                        self.findings.append(Finding(
                            severity=Severity.CRITICAL,
                            title="Potential Reentrancy",
                            description="External call detected with potential state changes after. Follow Checks-Effects-Interactions pattern.",
                            line=line_num,
                            code=line.strip(),
                            recommendation="Move state changes before external calls, or use ReentrancyGuard."
                        ))
                        break

    def _check_tx_origin(self, line: str, line_num: int):
        """Detect tx.origin usage for authentication."""
        if re.search(r'tx\.origin', line):
            if re.search(r'(require|if|assert).*tx\.origin', line):
                self.findings.append(Finding(
                    severity=Severity.HIGH,
                    title="tx.origin Authentication",
                    description="tx.origin used for authentication is vulnerable to phishing attacks.",
                    line=line_num,
                    code=line.strip(),
                    recommendation="Use msg.sender instead of tx.origin for authentication."
                ))

    def _check_unchecked_call(self, line: str, line_num: int):
        """Detect unchecked low-level call return values."""
        if re.search(r'\.call\(', line) or re.search(r'\.call\{', line):
            if not re.search(r'\(bool\s+\w+,', line) and not re.search(r'require\(', line):
                self.findings.append(Finding(
                    severity=Severity.HIGH,
                    title="Unchecked Call Return Value",
                    description="Low-level call return value not checked.",
                    line=line_num,
                    code=line.strip(),
                    recommendation="Check the return value: (bool success,) = addr.call{...}(...); require(success);"
                ))

    def _check_floating_pragma(self, line: str, line_num: int):
        """Detect floating pragma versions."""
        if re.search(r'pragma\s+solidity\s*\^', line):
            self.findings.append(Finding(
                severity=Severity.LOW,
                title="Floating Pragma",
                description="Floating pragma version allows compilation with different compiler versions.",
                line=line_num,
                code=line.strip(),
                recommendation="Use fixed pragma version: pragma solidity 0.8.20;"
            ))

    def _check_deprecated_functions(self, line: str, line_num: int):
        """Detect deprecated function usage."""
        deprecated = {
            'block.blockhash': 'blockhash()',
            'msg.gas': 'gasleft()',
            'throw': 'revert()',
            'sha3': 'keccak256()',
            'suicide': 'selfdestruct()',
        }

        for old, new in deprecated.items():
            if old in line:
                self.findings.append(Finding(
                    severity=Severity.INFO,
                    title="Deprecated Function",
                    description=f"'{old}' is deprecated.",
                    line=line_num,
                    code=line.strip(),
                    recommendation=f"Use '{new}' instead."
                ))

    def _check_hardcoded_addresses(self, line: str, line_num: int):
        """Detect hardcoded addresses."""
        if re.search(r'0x[a-fA-F0-9]{40}', line):
            if not re.search(r'address\(0\)|address\(0x0\)', line):
                self.findings.append(Finding(
                    severity=Severity.INFO,
                    title="Hardcoded Address",
                    description="Hardcoded address detected. Consider using immutable variables or constructor parameters.",
                    line=line_num,
                    code=line.strip(),
                    recommendation="Use constructor parameters or immutable variables for addresses."
                ))

    def _check_assembly(self, line: str, line_num: int):
        """Flag assembly usage for manual review."""
        if re.search(r'\bassembly\s*\{', line):
            self.findings.append(Finding(
                severity=Severity.INFO,
                title="Inline Assembly",
                description="Inline assembly detected. Requires careful manual review.",
                line=line_num,
                code=line.strip(),
                recommendation="Ensure assembly code is thoroughly reviewed and tested."
            ))

    def _check_selfdestruct(self, line: str, line_num: int):
        """Detect selfdestruct usage."""
        if re.search(r'\bselfdestruct\s*\(', line):
            self.findings.append(Finding(
                severity=Severity.MEDIUM,
                title="Selfdestruct Usage",
                description="selfdestruct can permanently destroy the contract and forcibly send ETH.",
                line=line_num,
                code=line.strip(),
                recommendation="Ensure selfdestruct is properly access-controlled and intended."
            ))

    def _check_delegatecall(self, line: str, line_num: int):
        """Detect delegatecall usage."""
        if re.search(r'\.delegatecall\(', line):
            self.findings.append(Finding(
                severity=Severity.HIGH,
                title="Delegatecall Usage",
                description="delegatecall executes code in calling contract's context. High risk of storage collision or malicious code execution.",
                line=line_num,
                code=line.strip(),
                recommendation="Ensure delegatecall target is trusted and storage layout is compatible."
            ))

    def _check_block_timestamp(self, line: str, line_num: int):
        """Detect block.timestamp usage in comparisons."""
        if re.search(r'block\.timestamp\s*[<>=!]+', line):
            self.findings.append(Finding(
                severity=Severity.LOW,
                title="Timestamp Dependence",
                description="block.timestamp can be manipulated by miners within ~15 seconds.",
                line=line_num,
                code=line.strip(),
                recommendation="Avoid using block.timestamp for critical logic. Consider block.number for longer timeframes."
            ))

    def _check_missing_reentrancy_guard(self, content: str, lines: List[str]):
        """Check if contract has external calls but no reentrancy guard."""
        has_external_call = bool(re.search(r'\.call\{|\.call\(|\.transfer\(|\.send\(', content))
        has_guard = bool(re.search(r'ReentrancyGuard|nonReentrant', content))

        if has_external_call and not has_guard:
            self.findings.append(Finding(
                severity=Severity.MEDIUM,
                title="Missing Reentrancy Guard",
                description="Contract has external calls but no ReentrancyGuard.",
                line=0,
                code="",
                recommendation="Consider using OpenZeppelin's ReentrancyGuard for functions with external calls."
            ))

    def _check_external_calls_in_loop(self, content: str, lines: List[str]):
        """Detect external calls inside loops (DoS risk)."""
        in_loop = False
        loop_start = 0

        for i, line in enumerate(lines, 1):
            if re.search(r'\b(for|while)\s*\(', line):
                in_loop = True
                loop_start = i

            if in_loop:
                if re.search(r'\.call\{|\.call\(|\.transfer\(|\.send\(', line):
                    self.findings.append(Finding(
                        severity=Severity.MEDIUM,
                        title="External Call in Loop",
                        description="External call inside loop can cause DoS if any call fails.",
                        line=i,
                        code=line.strip(),
                        recommendation="Use pull pattern instead of push pattern for payments."
                    ))

            if in_loop and '}' in line:
                in_loop = False

    def generate_report(self, filepath: Path) -> str:
        """Generate a markdown report of findings."""
        report = [
            f"# Security Scan Report",
            f"\n**File**: `{filepath}`",
            f"\n**Findings**: {len(self.findings)}",
            "",
        ]

        # Count by severity
        severity_counts = {}
        for finding in self.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

        report.append("## Summary")
        report.append("")
        report.append("| Severity | Count |")
        report.append("|----------|-------|")
        for sev in Severity:
            count = severity_counts.get(sev, 0)
            if count > 0:
                report.append(f"| {sev.value} | {count} |")

        report.append("")
        report.append("## Findings")
        report.append("")

        for i, finding in enumerate(self.findings, 1):
            report.append(f"### [{finding.severity.value}] {finding.title}")
            report.append("")
            if finding.line > 0:
                report.append(f"**Location**: Line {finding.line}")
            report.append(f"\n**Description**: {finding.description}")
            if finding.code:
                report.append(f"\n**Code**:")
                report.append(f"```solidity")
                report.append(finding.code)
                report.append(f"```")
            report.append(f"\n**Recommendation**: {finding.recommendation}")
            report.append("")

        return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Usage: python security_scan.py <contract.sol|directory>")
        sys.exit(1)

    target = Path(sys.argv[1])
    scanner = SecurityScanner()

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.sol"))
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    for filepath in files:
        print(f"\n{'='*60}")
        print(f"Scanning: {filepath}")
        print('='*60)

        findings = scanner.scan_file(filepath)
        report = scanner.generate_report(filepath)
        print(report)

        # Summary
        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in findings if f.severity == Severity.HIGH)

        if critical > 0:
            print(f"\n⚠️  {critical} CRITICAL issues found!")
        if high > 0:
            print(f"\n⚠️  {high} HIGH severity issues found!")


if __name__ == "__main__":
    main()
