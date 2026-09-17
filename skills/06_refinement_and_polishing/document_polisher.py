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

        # 4. AOD (Architecture Overview Diagram) 专属规范深度审计 (IBM 标准)
        if "architecture-overview" in file_path.name.lower() or "aod" in file_path.name.lower():
            # 检查是否混入具体物理软件反模式
            physical_stack_anti_patterns = re.findall(
                r"\b(mysql|postgresql|redis|kafka|nginx|docker|spring boot|mongodb|rocketmq)\b",
                content,
                re.IGNORECASE
            )
            if physical_stack_anti_patterns:
                score -= 15
                suggestions.append(f"AOD 混入具体物理技术栈反模式: {set(physical_stack_anti_patterns)}，应抽象为逻辑能力")

            # 检查是否有图例 Legend
            has_legend = bool(re.search(r"(Legend|架构图例)", content, re.IGNORECASE))
            if not has_legend:
                score -= 10
                suggestions.append("AOD 缺少统一架构图例 (Legend)，每种线条与颜色必须自解释")

            # 检查是否包含横切关注点
            has_cross_cutting = bool(re.search(r"(Cross-Cutting|横切关注点|横切守护)", content, re.IGNORECASE))
            if not has_cross_cutting:
                score -= 10
                suggestions.append("AOD 缺少横切关注点底座 (Cross-Cutting Concerns: 安全/可观测/高可用)")

            # 检查是否包含 3 分钟压力测试 (The 3-Minute Test)
            if file_path.suffix.lower() == ".md":
                has_3min_test = bool(re.search(r"(3-Minute Test|3分钟|白板复述)", content, re.IGNORECASE))
                if not has_3min_test:
                    score -= 10
                    suggestions.append("AOD 缺少合格性 '3 分钟压力测试' (The 3-Minute Test) 评审自检表")

        # 5. CM (Component Model) 专属规范深度审计 (IBM 标准: 逻辑/物理双层演进与契约优先)
        if "component-model" in file_path.name.lower():
            # 检查是否包含逻辑与物理双层演进
            has_dual_cm = bool(re.search(r"(Logical CM|逻辑组件)", content, re.IGNORECASE)) and \
                          bool(re.search(r"(Physical CM|物理组件)", content, re.IGNORECASE))
            if not has_dual_cm and file_path.suffix.lower() == ".md":
                score -= 15
                suggestions.append("CM 缺少 Logical CM (逻辑组件) 与 Physical CM (物理组件) 的双层演进映射")

            # 检查是否明确标注 Provided 与 Required 接口
            has_interfaces = bool(re.search(r"(Provided|提供接口)", content, re.IGNORECASE)) and \
                             bool(re.search(r"(Required|依赖接口)", content, re.IGNORECASE))
            if not has_interfaces:
                score -= 15
                suggestions.append("CM 缺少明确的 Provided (提供接口) 与 Required (依赖接口) 契约定义")

            # 检查是否有数据所有权定义 (Data Ownership)
            has_data_ownership = bool(re.search(r"(Data Ownership|数据归属|数据所有权)", content, re.IGNORECASE))
            if not has_data_ownership and file_path.suffix.lower() == ".md":
                score -= 10
                suggestions.append("CM 缺少组件领域数据排他性所有权归属 (Data Ownership Matrix)")

            # 检查是否有三道防线自检
            if file_path.suffix.lower() == ".md":
                has_three_defenses = bool(re.search(r"(三道防线|Team Allocation|团队分配|变更隔离)", content, re.IGNORECASE))
                if not has_three_defenses:
                    score -= 10
                    suggestions.append("CM 缺少 '三道防线' (团队分配测试、变更隔离测试、OM衔接测试) 评审自检表")

        # 6. OM (Operational Model) 专属规范深度审计 (IBM 标准: 逻辑/物理运行拓扑、CM映射与容灾)
        if "operational-model" in file_path.name.lower() or "deployment-model" in file_path.name.lower():
            # 检查是否包含逻辑与物理运行模型双层演进
            has_dual_om = bool(re.search(r"(Logical OM|逻辑运行)", content, re.IGNORECASE)) and \
                          bool(re.search(r"(Physical OM|物理运行|物理拓扑)", content, re.IGNORECASE))
            if not has_dual_om and file_path.suffix.lower() == ".md":
                score -= 15
                suggestions.append("OM 缺少 Logical OM (逻辑运行模型) 与 Physical OM (物理运行模型) 的双层演进映射")

            # 检查是否包含 CM 部署单元映射 (Deployment Allocation)
            has_cm_mapping = bool(re.search(r"(CM 映射|承载组件|Deployment Allocation|部署映射)", content, re.IGNORECASE))
            if not has_cm_mapping and file_path.suffix.lower() == ".md":
                score -= 15
                suggestions.append("OM 缺少与 CM 物理构建物的部署单元映射 (Deployment Allocation Matrix)")

            # 检查是否包含节点规范卡片 (Node Specification)
            has_node_spec = bool(re.search(r"(Node Specification|节点规范卡片|NODE-)", content, re.IGNORECASE))
            if not has_node_spec and file_path.suffix.lower() == ".md":
                score -= 10
                suggestions.append("OM 缺少标准节点规范卡片集 (Node Specifications: 标明机型规格、VPC/网络区域及存储配置)")

            # 检查是否落实高可用与容灾指标 (RTO / RPO)
            has_rto_rpo = bool(re.search(r"\bRTO\b", content)) and bool(re.search(r"\bRPO\b", content))
            if not has_rto_rpo and file_path.suffix.lower() == ".md":
                score -= 10
                suggestions.append("OM 缺少高可用容灾关键指标落地设计 (RTO 与 RPO)")

            # 检查是否包含压力实战测试 (拔电源测试 / 容量测算)
            if file_path.suffix.lower() == ".md":
                has_stress_test = bool(re.search(r"(拔电源|Chaos|Failure Scenario|实战测试)", content, re.IGNORECASE))
                if not has_stress_test:
                    score -= 10
                    suggestions.append("OM 缺少合格性 '压力实战测试' (拔电源演练、容量成本测算、运维可观测性就绪) 记录")

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
