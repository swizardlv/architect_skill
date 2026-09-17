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

        # 7. AD/ADR (Architecture Decision Record) 专属规范深度审计 (IBM 标准: 权衡闭环、多方案与代价缓解)
        is_adr_file = (
            file_path.name.lower().startswith("adr-") or "/adrs/" in str(file_path).lower()
        ) and "adr-index" not in file_path.name.lower()

        if is_adr_file and file_path.suffix.lower() == ".md":
            # 检查状态与元数据
            has_status_and_owner = bool(
                re.search(r"(状态|Status)[^\n:]*[:*]+\s*(Proposed|Accepted|Rejected|Deprecated|Superseded|提议|已接受|已废弃|被取代)", content, re.IGNORECASE)
            ) and bool(re.search(r"(决策人|决策责任人|Owner|Architect)", content, re.IGNORECASE))
            if not has_status_and_owner:
                score -= 10
                suggestions.append("ADR 缺少标准状态生命周期元数据 (Proposed/Accepted/Deprecated/Superseded) 或决策责任人")

            # 检查备选方案客观评估与对比矩阵
            has_alternatives = bool(re.search(r"(备选方案|Options Considered|候选方案)", content, re.IGNORECASE))
            has_comparison_matrix = bool(re.search(r"\|.*(对比|Trade-off|方案).*\|", content, re.IGNORECASE))
            has_rejection_reason = bool(re.search(r"(否决|Rejected|被否决)", content, re.IGNORECASE))
            if not (has_alternatives and (has_comparison_matrix or has_rejection_reason)):
                score -= 15
                suggestions.append("ADR 缺少客观的备选方案多维对比矩阵 (Trade-off Matrix) 或被否决方案根因分析")

            # 检查负面代价与工程妥协 (严禁一言堂与不谈代价)
            has_tradeoffs = bool(re.search(r"(代价|负向妥协|负面代价|Negative Consequences|Trade-offs?)", content, re.IGNORECASE))
            if not has_tradeoffs:
                score -= 15
                suggestions.append("ADR 缺少显式的负面代价与技术妥协 (Negative Consequences & Trade-offs) 剖析")

            # 检查工程缓解与补偿策略 (Mitigations)
            has_mitigation = bool(re.search(r"(缓解|Mitigation|兜底|补偿策略)", content, re.IGNORECASE))
            if not has_mitigation:
                score -= 15
                suggestions.append("ADR 缺少针对负面代价的具体工程缓解与补偿防线 (Mitigations & Compensating Controls)")

            # 检查落地遵从性与架构守护
            has_compliance = bool(re.search(r"(遵从性|Compliance|架构守护|验证检查|静态架构规则)", content, re.IGNORECASE))
            if not has_compliance:
                score -= 10
                suggestions.append("ADR 缺少自动化落地遵从性与架构守护检查清单 (Compliance Verification)")

        # 8. ARC (Architecture Requirements Checklist) 专属规范深度审计 (IBM URPS+ 标准)
        is_arc_file = "requirements-checklist" in file_path.name.lower() or "arc-" in file_path.name.lower()

        if is_arc_file and file_path.suffix.lower() == ".md":
            # 检查 URPS+ 维度覆盖
            has_urps_perf = bool(re.search(r"(Performance|性能|吞吐|时延|Latency|TPS|QPS)", content, re.IGNORECASE))
            has_urps_avail = bool(re.search(r"(Availability|可用性|容灾|Resiliency|RTO|RPO|SLA)", content, re.IGNORECASE))
            has_urps_sec = bool(re.search(r"(Security|安全|合规|Compliance|mTLS|HSM|加密)", content, re.IGNORECASE))
            has_urps_ops = bool(re.search(r"(Observability|Manageability|可观测|运维|Trace|监控|APM)", content, re.IGNORECASE))
            has_urps_int = bool(re.search(r"(Integrability|Portability|集成|可移植|协议|兼容)", content, re.IGNORECASE))

            missing_dims = []
            if not has_urps_perf:
                missing_dims.append("Performance")
            if not has_urps_avail:
                missing_dims.append("Availability")
            if not has_urps_sec:
                missing_dims.append("Security")
            if not (has_urps_ops or has_urps_int):
                missing_dims.append("Observability/Integrability")

            if len(missing_dims) >= 2:
                score -= 15
                suggestions.append(f"ARC 缺少关键 URPS+ 质量属性维度覆盖: {missing_dims}")

            # 检查是否有场景化表达 (SEI 6 要素或 Scenario)
            has_scenario = bool(re.search(r"(Scenario|场景|刺激|Stimulus|Response)", content, re.IGNORECASE))
            if not has_scenario:
                score -= 10
                suggestions.append("ARC 缺少 SEI 场景化表达 (Quality Attribute Scenario: 刺激源、刺激、环境与响应)")

            # 检查是否包含架构推导映射 (Mapping to CM / OM / ADR)
            has_mapping = bool(re.search(r"(CM|OM|ADR|架构推导|设计映射|Mapping)", content))
            if not has_mapping:
                score -= 15
                suggestions.append("ARC 缺少与下游架构设计 (CM 组件 / OM 拓扑 / ADR 决策) 的双向推导映射")

            # 检查量化指标度量与验收手段
            has_quantified_metrics = bool(re.search(r"(P9[0-9]|TPS|QPS|RTO|RPO|µs|ms|%|SLA)", content))
            if not has_quantified_metrics:
                score -= 15
                suggestions.append("ARC 缺少可测试量化指标 (如 P99, TPS, RTO, RPO, µs)，存在空泛描述")

            # 检查闭环状态与验证方法
            has_status_and_verify = bool(re.search(r"(Verified|Approved|Closed|已验证|已批准|关闭|Status|状态)", content, re.IGNORECASE)) and \
                                    bool(re.search(r"(验证|Verification|压测|演练|测试|Benchmark)", content, re.IGNORECASE))
            if not has_status_and_verify:
                score -= 10
                suggestions.append("ARC 缺少明确的自动化验证方式或闭环跟踪状态 (Status: Verified/Approved/Closed)")

        # 9. Business Drivers / Goals 专属规范深度审计 (IBM 商业目标第一源头标准)
        is_drivers_file = "business-driver" in file_path.name.lower() or "business-goal" in file_path.name.lower()

        if is_drivers_file and file_path.suffix.lower() == ".md":
            # 检查是否为商业结果驱动 (Outcome-driven)
            has_outcomes = bool(re.search(r"(Outcome|商业回报|商业价值|战略回报|ROI|收益)", content, re.IGNORECASE))
            if not has_outcomes:
                score -= 15
                suggestions.append("业务目标缺少明确的商业回报与成果导向 (Outcome-driven) 阐述")

            # 检查 SMART 量化指标与优先级
            has_smart_metrics = bool(re.search(r"(\d+%|\d+倍|TPS|P9[0-9]|P0|P1|优先级|SMART)", content))
            if not has_smart_metrics:
                score -= 15
                suggestions.append("业务目标缺少量化基准 (SMART 指标) 或优先级排序 (P0/P1)")

            # 检查“为什么重要”逆向穿透或架构重大性筛选
            has_significance_filter = bool(re.search(r"(So What|为什么重要|架构重大性|Significance Filtering|重大架构)", content, re.IGNORECASE))
            if not has_significance_filter:
                score -= 10
                suggestions.append("业务目标缺少'为什么重要'逆向穿透测试 (The So What? Test) 或架构重大性筛选表")

            # 检查架构驱动力矩阵 (Driver Matrix 映射)
            has_driver_matrix = bool(re.search(r"(Driver Matrix|架构驱动力|驱动的架构关注点|Architectural Impact)", content, re.IGNORECASE))
            if not has_driver_matrix:
                score -= 10
                suggestions.append("业务目标缺少结构化的架构驱动力矩阵 (Driver Matrix) 映射至 CM/OM/ADR")

            # 检查业务赞助人双向确认 (Playback & Sign-off)
            has_playback = bool(re.search(r"(Playback|双向确认|业务赞助人|Sponsor Sign-off|对齐签署)", content, re.IGNORECASE))
            if not has_playback:
                score -= 10
                suggestions.append("业务目标缺少业务赞助人双向确认与冻结签署 (Playback & Sponsor Sign-off)")

        # 10. Constraints & Assumptions 专属规范深度审计 (IBM 不可逾越边界三大范畴标准)
        is_constraints_file = "constraints" in file_path.name.lower() or "invariants" in file_path.name.lower()

        if is_constraints_file and file_path.suffix.lower() == ".md":
            # 检查三大分类覆盖 (BC/TC/LC)
            has_bc = bool(re.search(r"(组织约束|业务约束|交付时间|时间窗口|团队技能|康威定律|BC-)", content, re.IGNORECASE))
            has_tc = bool(re.search(r"(技术约束|遗留资产|利旧|既有系统|部署环境|硬件|TC-)", content, re.IGNORECASE))
            has_lc = bool(re.search(r"(合规|监管|法律|数据主权|GDPR|牌照|审计|LC-)", content, re.IGNORECASE))

            missing_constraint_types = []
            if not has_bc:
                missing_constraint_types.append("业务与组织约束 (BC)")
            if not has_tc:
                missing_constraint_types.append("技术与遗留资产约束 (TC)")
            if not has_lc:
                missing_constraint_types.append("法律合规监管红线 (LC)")

            if missing_constraint_types:
                score -= 15
                suggestions.append(f"约束条件缺少关键范畴覆盖: {missing_constraint_types}")

            # 检查约束与选择区分检验 (Constraint vs Decision Test)
            has_decision_distinction = bool(re.search(r"(Constraint vs|约束与决策|约束与选择|个人技术偏好|区分检验)", content, re.IGNORECASE))
            if not has_decision_distinction:
                score -= 10
                suggestions.append("缺少'约束与选择区分检验' (Constraint vs. Decision Test)，未能有效排除个人技术偏好")

            # 检查显式假设的失效触发条件 (Invalidation Trigger)
            has_assumptions = bool(re.search(r"(假设|Assumption|ASM-)", content, re.IGNORECASE))
            has_invalidation_trigger = bool(re.search(r"(失效触发|Invalidation Trigger|失效后)", content, re.IGNORECASE))
            if has_assumptions and not has_invalidation_trigger:
                score -= 10
                suggestions.append("核心架构假设缺少明确的失效触发条件 (Invalidation Trigger) 与演进应对预案")

        # 11. System Context / Overview 专属规范深度审计 (IBM Level 0 绝对黑盒标准)
        is_context_file = "system-context" in file_path.name.lower() or "system-overview" in file_path.name.lower() or "c4-context" in file_path.name.lower()

        if is_context_file and file_path.suffix.lower() == ".md":
            # 检查 X-Ray 违规反模式 (严禁泄露内部微服务、内部数据库或内部子分层)
            internal_xray_patterns = re.findall(
                r"\b(Ingress Gateway Tier|Matching Engine Core|Sequencer Hub|GatewayCtx|MatchingCtx|ConsensusCtx|内部数据库|MySQL|PostgreSQL|Redis|Kafka|Disruptor RingBuffer)\b",
                content,
                re.IGNORECASE
            )
            if internal_xray_patterns:
                score -= 20
                suggestions.append(f"系统上下文触犯'X射线'违规反模式: 出现内部组件细节 {set(internal_xray_patterns)}，Level 0 必须为绝对黑盒")

            # 检查中心系统是否为单一黑盒实体 (In-Scope)
            has_single_system = bool(re.search(r"(单一黑盒|中心系统|In-Scope|The System|中心黑盒)", content, re.IGNORECASE))
            if not has_single_system:
                score -= 10
                suggestions.append("系统上下文缺少明确的中心黑盒实体定义 (In-Scope 单一系统边界)")

            # 检查上下文实体交互矩阵 (Context Interaction Matrix)
            has_context_matrix = bool(re.search(r"\|.*(实体分类|外部角色|外部系统|In-Scope|Out-of-Scope).*\|", content, re.IGNORECASE))
            if not has_context_matrix:
                score -= 15
                suggestions.append("系统上下文缺少结构化的'上下文实体交互矩阵' (Context Interaction Matrix)")

            # 检查外部角色与外部系统依赖的区分
            has_actors = bool(re.search(r"(外部参与者|外部角色|Actors?|干系人)", content, re.IGNORECASE))
            has_ext_systems = bool(re.search(r"(外部系统|External Systems?|依赖系统|既有资产|Legacy)", content, re.IGNORECASE))
            if not (has_actors and has_ext_systems):
                score -= 10
                suggestions.append("系统上下文未清晰区分'外部角色 (Actors)'与'外部系统依赖 (External Systems)'")

            # 检查三道安检门与 Zooming In 过渡说明
            has_gatekeeper_or_zoom = bool(re.search(r"(X-Ray|安检门|Who owns this|孤岛|Zooming In|万米高空|AOD.*过渡)", content, re.IGNORECASE))
            if not has_gatekeeper_or_zoom:
                score -= 10
                suggestions.append("系统上下文缺少三道安检门检验记录或向 AOD 缩放过渡说明 (Zooming In)")

        # 12. Architectural Style Selection 专属规范深度审计 (IBM 骨骼结构与宏观模式选型标准)
        is_style_file = "architectural-style" in file_path.name.lower() or "style-selection" in file_path.name.lower()

        if is_style_file and file_path.suffix.lower() == ".md":
            # 检查是否区分宏观主导风格与局部微模式
            has_macro_style = bool(re.search(r"(宏观主导|Primary Style|Macro Style|主导架构风格)", content, re.IGNORECASE))
            has_local_patterns = bool(re.search(r"(局部架构模式|Local Patterns?|微模式|局部模式)", content, re.IGNORECASE))
            if not (has_macro_style and has_local_patterns):
                score -= 15
                suggestions.append("架构风格选型未清晰界定'宏观主导架构风格 (Macro Style)'与子域的'局部微模式 (Local Patterns)'")

            # 检查是否强绑定 ARC 质量属性指标
            has_arc_mapping = bool(re.search(r"(ARC-|质量属性驱动|NFR-)", content))
            if not has_arc_mapping:
                score -= 15
                suggestions.append("架构风格选型缺少与 ARC 质量指标 (如 ARC-PERF, ARC-AVAIL) 的显式驱动映射")

            # 检查候选架构风格横向权衡对比矩阵
            has_tradeoff_matrix = bool(re.search(r"\|.*(候选|备选|评估维度|风格|Trade-off).*\|", content, re.IGNORECASE)) and \
                                  bool(re.search(r"(否决|Rejected|被否决)", content, re.IGNORECASE))
            if not has_tradeoff_matrix:
                score -= 15
                suggestions.append("架构风格选型缺少候选风格横向权衡对比矩阵 (Trade-off Matrix) 或被否决根因分析")

            # 检查五维评判漏斗自检
            has_funnel = bool(re.search(r"(五维|漏斗|团队能力|逆转成本|TCO|Feasibility|Reversibility)", content, re.IGNORECASE))
            if not has_funnel:
                score -= 10
                suggestions.append("架构风格选型缺少'五维评判漏斗' (团队可行性、NFR拟合、逆转成本、TCO预算、ADR闭环) 自检表")

            # 检查是否明确关联顶层 ADR 闭环
            has_adr_ref = bool(re.search(r"(ADR-|AD-|架构决策记录)", content))
            if not has_adr_ref:
                score -= 10
                suggestions.append("架构风格选型未明确关联顶层架构决策记录 (ADR-001 等)")

        # 13. Conceptual Data Model (CDM) 专属规范深度审计 (IBM 业务数据视角顶层抽象标准)
        is_cdm_file = "conceptual-data-model" in file_path.name.lower() or "cdm" in file_path.name.lower()

        if is_cdm_file and file_path.suffix.lower() == ".md":
            # 检查技术中立性反模式 (严禁出现物理数据库字段与特性)
            physical_db_patterns = re.findall(
                r"\b(auto_increment|varchar\(\d+\)|int64|int32|bigint|composite index|foreign key|redis key|mysql|postgresql|b-tree|lsm-tree)\b",
                content,
                re.IGNORECASE
            )
            if physical_db_patterns:
                score -= 20
                suggestions.append(f"CDM 混入物理数据库实现反模式: {set(physical_db_patterns)}，概念层必须保持技术中立")

            # 检查统一语言概念字典 (Ubiquitous Language Dictionary)
            has_term_dict = bool(re.search(r"\|.*(概念术语|统一语言|业务定义|Ubiquitous Language).*\|", content, re.IGNORECASE))
            if not has_term_dict:
                score -= 15
                suggestions.append("CDM 缺少结构化的'统一语言与领域概念字典' (Ubiquitous Language Dictionary)")

            # 检查概念 ER 图与基数标注 (Crow's Foot 或 Cardinality)
            has_er_diagram = "erDiagram" in content
            has_cardinality = bool(re.search(r"(\|\|--|--o\{|--\|\{|--\|\||1\.\.\*|0\.\.\*)", content))
            if not (has_er_diagram and has_cardinality):
                score -= 15
                suggestions.append("CDM 缺少标准 Mermaid 概念 ER 图 (erDiagram) 或精确的关系基数标注 (1, 0..1, 1..*, 0..*)")

            # 检查限界上下文与数据所有权矩阵 (Data Ownership Matrix)
            has_ownership_matrix = bool(re.search(r"\|.*(数据所有权|归属组件|限界上下文|Data Ownership).*\|", content, re.IGNORECASE))
            if not has_ownership_matrix:
                score -= 15
                suggestions.append("CDM 缺少'限界上下文与数据所有权矩阵' (Data Ownership Matrix: 映射至独占管理 CM 组件)")

            # 检查三步压力测试 (Business Proxy, Lifecycle, CM Driving)
            has_stress_tests = bool(re.search(r"(压力测试|业务代言人|走查|生命周期完整性|驱动组件模型|Walkthrough)", content, re.IGNORECASE))
            if not has_stress_tests:
                score -= 10
                suggestions.append("CDM 缺少合格性'三步压力测试' (业务走查、生命周期完整性、驱动 CM 验证) 自检记录")

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
