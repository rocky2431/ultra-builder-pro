#!/usr/bin/env python3
"""
Git Safety Check Script

Analyzes git operations for potential risks before execution.

Usage:
    python git_safety_check.py <git-command>
    python git_safety_check.py "git push --force origin main"
    python git_safety_check.py --analyze-repo
"""

import subprocess
import sys
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class RiskLevel(Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGEROUS = "DANGEROUS"
    BLOCKED = "BLOCKED"


@dataclass
class RiskAssessment:
    level: RiskLevel
    command: str
    warnings: List[str]
    recommendations: List[str]
    requires_confirmation: bool


class GitSafetyChecker:
    """Analyzes git commands for safety risks."""

    # High-risk patterns
    DANGEROUS_PATTERNS = [
        (r'push\s+--force\s+origin\s+(main|master)',
         "Force push to main/master rewrites shared history",
         ["Use --force-with-lease instead", "Coordinate with team first"]),

        (r'push\s+-f\s+origin\s+(main|master)',
         "Force push to main/master rewrites shared history",
         ["Use --force-with-lease instead", "Coordinate with team first"]),

        (r'reset\s+--hard\s+HEAD~',
         "Hard reset discards commits permanently",
         ["Ensure commits are backed up", "Consider git revert instead"]),

        (r'reset\s+--hard\s+origin/',
         "Hard reset to remote discards local changes",
         ["Stash changes first: git stash", "Verify no important uncommitted work"]),

        (r'clean\s+-fd',
         "Removes untracked files and directories permanently",
         ["Review untracked files first: git status", "Consider git stash -u"]),

        (r'branch\s+-D',
         "Force deletes branch even if not merged",
         ["Use -d for safe delete", "Verify branch is merged or backed up"]),
    ]

    # Caution patterns
    CAUTION_PATTERNS = [
        (r'rebase\s+',
         "Rebase rewrites commit history",
         ["Ensure branch is not shared", "Consider merge for shared branches"]),

        (r'push\s+--force-with-lease',
         "Force push with lease is safer but still rewrites history",
         ["Verify no one else has pushed", "Communicate with team"]),

        (r'cherry-pick\s+',
         "Cherry-pick may cause duplicate commits",
         ["Document the cherry-pick", "Consider if merge is better"]),

        (r'stash\s+drop',
         "Permanently removes stashed changes",
         ["Verify stash content first: git stash show -p"]),
    ]

    def analyze_command(self, command: str) -> RiskAssessment:
        """Analyze a git command for safety risks."""
        warnings = []
        recommendations = []
        level = RiskLevel.SAFE
        requires_confirmation = False

        # Check dangerous patterns
        for pattern, warning, recs in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                level = RiskLevel.DANGEROUS
                warnings.append(warning)
                recommendations.extend(recs)
                requires_confirmation = True

        # Check caution patterns (only if not already dangerous)
        if level == RiskLevel.SAFE:
            for pattern, warning, recs in self.CAUTION_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    level = RiskLevel.CAUTION
                    warnings.append(warning)
                    recommendations.extend(recs)

        return RiskAssessment(
            level=level,
            command=command,
            warnings=warnings,
            recommendations=recommendations,
            requires_confirmation=requires_confirmation
        )

    def analyze_repo_state(self) -> dict:
        """Analyze current repository state for potential issues."""
        results = {
            "branch": self._get_current_branch(),
            "uncommitted_changes": self._has_uncommitted_changes(),
            "unpushed_commits": self._count_unpushed_commits(),
            "stash_count": self._count_stashes(),
            "warnings": [],
            "recommendations": []
        }

        # Check for issues
        if results["uncommitted_changes"]:
            results["warnings"].append("Uncommitted changes detected")
            results["recommendations"].append("Commit or stash changes before risky operations")

        if results["unpushed_commits"] > 5:
            results["warnings"].append(f"{results['unpushed_commits']} unpushed commits")
            results["recommendations"].append("Consider pushing more frequently")

        if results["branch"] in ["main", "master"]:
            results["warnings"].append("Working directly on main/master branch")
            results["recommendations"].append("Create a feature branch for changes")

        return results

    def _get_current_branch(self) -> str:
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def _has_uncommitted_changes(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def _count_unpushed_commits(self) -> int:
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "@{u}..HEAD"],
                capture_output=True, text=True, check=True
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError:
            return 0

    def _count_stashes(self) -> int:
        try:
            result = subprocess.run(
                ["git", "stash", "list"],
                capture_output=True, text=True, check=True
            )
            return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except subprocess.CalledProcessError:
            return 0


def format_assessment(assessment: RiskAssessment) -> str:
    """Format assessment for display."""
    icons = {
        RiskLevel.SAFE: "✅",
        RiskLevel.CAUTION: "⚠️",
        RiskLevel.DANGEROUS: "🚨",
        RiskLevel.BLOCKED: "🛑"
    }

    lines = [
        f"\n{'='*50}",
        f"Git Safety Check",
        f"{'='*50}",
        f"",
        f"Command: {assessment.command}",
        f"Risk Level: {icons[assessment.level]} {assessment.level.value}",
    ]

    if assessment.warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in assessment.warnings:
            lines.append(f"  - {warning}")

    if assessment.recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for rec in assessment.recommendations:
            lines.append(f"  - {rec}")

    if assessment.requires_confirmation:
        lines.append("")
        lines.append("⚠️  This operation requires explicit confirmation")

    lines.append(f"{'='*50}")
    return "\n".join(lines)


def format_repo_state(state: dict) -> str:
    """Format repo state for display."""
    lines = [
        f"\n{'='*50}",
        f"Repository State Analysis",
        f"{'='*50}",
        f"",
        f"Current branch: {state['branch']}",
        f"Uncommitted changes: {'Yes' if state['uncommitted_changes'] else 'No'}",
        f"Unpushed commits: {state['unpushed_commits']}",
        f"Stashes: {state['stash_count']}",
    ]

    if state["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        for warning in state["warnings"]:
            lines.append(f"  ⚠️  {warning}")

    if state["recommendations"]:
        lines.append("")
        lines.append("Recommendations:")
        for rec in state["recommendations"]:
            lines.append(f"  - {rec}")

    lines.append(f"{'='*50}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python git_safety_check.py <git-command>")
        print("  python git_safety_check.py --analyze-repo")
        sys.exit(1)

    checker = GitSafetyChecker()

    if sys.argv[1] == "--analyze-repo":
        state = checker.analyze_repo_state()
        print(format_repo_state(state))
    else:
        command = " ".join(sys.argv[1:])
        assessment = checker.analyze_command(command)
        print(format_assessment(assessment))

        # Exit with non-zero if dangerous
        if assessment.level == RiskLevel.DANGEROUS:
            sys.exit(1)


if __name__ == "__main__":
    main()
