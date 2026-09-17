"""架构文档质量审查与深化检查引擎 (Architecture Document Polishing Engine).

提供对四层系统架构文档深度与精细度的自动化审查与指标度量能力，
杜绝空泛粗糙、占位符残留与缺乏工程落地参数等质量缺陷。
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class DocumentQualityReport:
    file_path: str
    line_count: int
    has_diagrams: bool
    has_tables: bool
    has_code_or_ddl: bool
    placeholders_found: List[str]
    score: int  # 0 - 100
    suggestions: List[str]


class ArchitectureDocumentPolisher:
    """架构文档精细度审查与质量分析器."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.ws = Path(workspace_root).resolve()

    def audit_workspace(self) -> Tuple[bool, List[DocumentQualityReport]]:
        """对工作区内所有架构 markdown 文档进行质量审计."""
        reports: List[DocumentQualityReport] = []
        all_passed = True

        for md_file in sorted(self.ws.rglob("*.md")):
            if md_file.name.startswith(".") or "archive" in str(md_file):
                continue
            report = self.audit_file(md_file)
            reports.append(report)
            if report.score < 70:
                all_passed = False

        return all_passed, reports

    def audit_file(self, file_path: Path) -> DocumentQualityReport:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        line_count = len(lines)

        has_diagrams = "```mermaid" in content
        has_tables = bool(re.search(r"\|.*\|.*\|", content))
        has_code_or_ddl = bool(re.search(r"```(sql|json|yaml|go|rust|python|bash)", content))

        # 检查未替换的模板占位符
        placeholders = re.findall(r"(\[待补充.*?\]|\[例如.*?\]|\{.*?待定.*?\}|TODO|TBD)", content)

        score = 100
        suggestions: List[str] = []

        # 1. 行数与篇幅检测
        if line_count < 25:
            score -= 30
            suggestions.append("文档篇幅过短 (<25行)，内容可能偏粗糙，缺少必要的设计细节与推导")
        elif line_count < 40:
            score -= 15
            suggestions.append("建议进一步扩充技术参数、异常处理与边界场景说明")

        # 2. 占位符扣分
        if placeholders:
            score -= min(30, len(placeholders) * 10)
            suggestions.append(f"发现未替换的模板占位符: {placeholders[:3]}")

        # 3. 缺乏结构化表达扣分
        if not has_tables and not has_diagrams and not has_code_or_ddl:
            score -= 20
            suggestions.append("缺乏表格、图元或代码/DDL等结构化工程表达，纯文字叙述不利于评审")

        score = max(0, min(100, score))

        return DocumentQualityReport(
            file_path=str(file_path.relative_to(self.ws)),
            line_count=line_count,
            has_diagrams=has_diagrams,
            has_tables=has_tables,
            has_code_or_ddl=has_code_or_ddl,
            placeholders_found=placeholders,
            score=score,
            suggestions=suggestions,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="架构文档精细度审查与质量分析工具")
    parser.add_argument("workspace", help="架构文档根目录 (如 docs/architecture)")
    args = parser.parse_args()

    polisher = ArchitectureDocumentPolisher(args.workspace)
    passed, reports = polisher.audit_workspace()

    print("\n" + "=" * 70)
    print("📋 架构文档质量精细度审查报告 (Documentation Polishing Report)")
    print("=" * 70)

    for r in reports:
        status_icon = "✅" if r.score >= 70 else "⚠️"
        print(f"{status_icon} [{r.score:3d}分] {r.file_path} ({r.line_count} 行)")
        for sug in r.suggestions:
            print(f"    👉 优化建议: {sug}")

    print("-" * 70)
    print(f"综合质量评定: {'通过 (PASS)' if passed else '需进一步打磨深化 (NEEDS REFINEMENT)'}\n")


if __name__ == "__main__":
    main()
