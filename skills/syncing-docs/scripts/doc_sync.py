#!/usr/bin/env python3
"""
Documentation Synchronization Script

Checks alignment between documentation and code.

Usage:
    python doc_sync.py check  # Check for drift
    python doc_sync.py create-adr <number> <title>  # Create new ADR
    python doc_sync.py list-adrs  # List all ADRs
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple


class DocSyncManager:
    """Manages documentation synchronization."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.adr_dir = self.project_path / ".ultra" / "docs" / "decisions"
        self.specs_dir = self.project_path / "specs"
        self.legacy_docs_dir = self.project_path / "docs"

    def check_drift(self) -> Dict:
        """Check for documentation drift."""
        result = {
            "specs_found": [],
            "missing_docs": [],
            "stale_markers": [],
            "undocumented_features": [],
            "adr_count": 0,
            "warnings": [],
            "recommendations": []
        }

        # Check specs directory
        for pattern in ["*.md"]:
            for doc in self.specs_dir.glob(pattern) if self.specs_dir.exists() else []:
                result["specs_found"].append(str(doc.relative_to(self.project_path)))
                self._check_stale_markers(doc, result)

        # Check legacy docs
        for pattern in ["*.md"]:
            for doc in self.legacy_docs_dir.glob(pattern) if self.legacy_docs_dir.exists() else []:
                result["specs_found"].append(str(doc.relative_to(self.project_path)))
                self._check_stale_markers(doc, result)

        # Count ADRs
        if self.adr_dir.exists():
            result["adr_count"] = len(list(self.adr_dir.glob("ADR-*.md")))

        # Check for common missing docs
        expected_docs = [
            ("specs/product.md", "Product requirements"),
            ("specs/architecture.md", "Architecture decisions"),
        ]

        for path, description in expected_docs:
            if not (self.project_path / path).exists():
                # Check legacy location
                legacy_paths = [
                    path.replace("specs/", "docs/"),
                    path.replace("product.md", "prd.md"),
                    path.replace("architecture.md", "tech.md"),
                ]
                found = any((self.project_path / lp).exists() for lp in legacy_paths)
                if not found:
                    result["missing_docs"].append(f"{path} ({description})")

        # Generate recommendations
        if result["stale_markers"]:
            result["recommendations"].append("Review and resolve [NEEDS CLARIFICATION] markers")

        if result["missing_docs"]:
            result["recommendations"].append("Create missing specification documents")

        if result["adr_count"] == 0:
            result["recommendations"].append("Consider documenting major decisions as ADRs")

        return result

    def _check_stale_markers(self, doc_path: Path, result: Dict):
        """Check for stale markers in documentation."""
        try:
            content = doc_path.read_text()
            markers = [
                r'\[NEEDS CLARIFICATION\]',
                r'\[TODO\]',
                r'\[TBD\]',
                r'\[PENDING\]',
            ]

            for marker in markers:
                matches = re.findall(marker, content, re.IGNORECASE)
                if matches:
                    result["stale_markers"].append({
                        "file": str(doc_path.relative_to(self.project_path)),
                        "marker": matches[0],
                        "count": len(matches)
                    })
        except:
            pass

    def create_adr(self, number: int, title: str) -> str:
        """Create a new ADR from template."""
        self.adr_dir.mkdir(parents=True, exist_ok=True)

        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        filename = f"ADR-{number:03d}-{slug}.md"
        filepath = self.adr_dir / filename

        template = f"""# ADR-{number:03d}: {title}

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** Proposed

## Context

[What situation led to this decision? What problem are we solving?]

## Decision

[What we decided to do. Be specific and actionable.]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

## Alternatives Considered

### Option A: [Name]
- **Pros:** [advantages]
- **Cons:** [disadvantages]
- **Why not:** [reason for rejection]

## References

- [Link to research]
- [Documentation]
"""

        filepath.write_text(template)
        return str(filepath)

    def list_adrs(self) -> List[Dict]:
        """List all ADRs with their status."""
        adrs = []

        if not self.adr_dir.exists():
            return adrs

        for adr_file in sorted(self.adr_dir.glob("ADR-*.md")):
            try:
                content = adr_file.read_text()

                # Extract title
                title_match = re.search(r'^#\s+ADR-\d+:\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else "Unknown"

                # Extract status
                status_match = re.search(r'\*\*Status:\*\*\s+(\w+)', content)
                status = status_match.group(1) if status_match else "Unknown"

                # Extract date
                date_match = re.search(r'\*\*Date:\*\*\s+([\d-]+)', content)
                date = date_match.group(1) if date_match else "Unknown"

                adrs.append({
                    "file": adr_file.name,
                    "title": title,
                    "status": status,
                    "date": date
                })
            except:
                pass

        return adrs


def format_drift_report(result: Dict) -> str:
    """Format drift check report."""
    lines = [
        "",
        "=" * 50,
        "文档同步检查",
        "=" * 50,
        "",
    ]

    if result["specs_found"]:
        lines.append("发现的规格文档:")
        for spec in result["specs_found"]:
            lines.append(f"  ✅ {spec}")
        lines.append("")

    if result["missing_docs"]:
        lines.append("缺少的文档:")
        for doc in result["missing_docs"]:
            lines.append(f"  ⚠️  {doc}")
        lines.append("")

    if result["stale_markers"]:
        lines.append("待处理标记:")
        for marker in result["stale_markers"]:
            lines.append(f"  ⚠️  {marker['file']}: {marker['count']}x {marker['marker']}")
        lines.append("")

    lines.append(f"ADR 数量: {result['adr_count']}")

    if result["recommendations"]:
        lines.append("")
        lines.append("建议:")
        for rec in result["recommendations"]:
            lines.append(f"  → {rec}")

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)


def format_adr_list(adrs: List[Dict]) -> str:
    """Format ADR list."""
    if not adrs:
        return "未找到 ADR 文档"

    lines = [
        "",
        "=" * 50,
        "架构决策记录 (ADRs)",
        "=" * 50,
        "",
    ]

    for adr in adrs:
        status_icon = {
            "Accepted": "✅",
            "Proposed": "📝",
            "Deprecated": "⚠️",
            "Superseded": "🔄"
        }.get(adr["status"], "❓")

        lines.append(f"{status_icon} {adr['file']}")
        lines.append(f"   {adr['title']}")
        lines.append(f"   状态: {adr['status']} | 日期: {adr['date']}")
        lines.append("")

    lines.append("=" * 50)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python doc_sync.py check")
        print("  python doc_sync.py create-adr <number> <title>")
        print("  python doc_sync.py list-adrs")
        sys.exit(1)

    manager = DocSyncManager()
    command = sys.argv[1]

    if command == "check":
        result = manager.check_drift()
        print(format_drift_report(result))

    elif command == "create-adr":
        if len(sys.argv) < 4:
            print("Usage: python doc_sync.py create-adr <number> <title>")
            sys.exit(1)
        number = int(sys.argv[2])
        title = " ".join(sys.argv[3:])
        filepath = manager.create_adr(number, title)
        print(f"✅ 已创建 ADR: {filepath}")

    elif command == "list-adrs":
        adrs = manager.list_adrs()
        print(format_adr_list(adrs))


if __name__ == "__main__":
    main()
