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

            # Agent AI 专属 AOD 深度审计 (快慢思考路由、安全围栏 Guardrails、HITL 逃生通道)
            is_agent_aod = bool(re.search(r"(Agent|智能体|认知路由|Intent Triage|LLM Gateway|Tool Sandbox|Prompt 注入)", content, re.IGNORECASE))
            if is_agent_aod:
                has_fast_slow = bool(re.search(r"(快慢思考|Fast-Slow|System 1|意图分流|Intent Triage|规则拦截)", content, re.IGNORECASE))
                if not has_fast_slow:
                    score -= 10
                    suggestions.append("Agent AOD 缺少'快慢思考意图分流层' (Intent Triage: 规则/小模型拦截 vs 深度推理分流)")

                has_guardrails = bool(re.search(r"(Guardrail|安全围栏|PII|Prompt.*注入|脱敏)", content, re.IGNORECASE))
                if not has_guardrails:
                    score -= 10
                    suggestions.append("Agent AOD 横切底座缺少显式'安全围栏 (Guardrails: Prompt 注入防护与 PII 脱敏)'")

                has_hitl_escape = bool(re.search(r"(HITL|人机协同|审批挂起|人工接管|Escalation)", content, re.IGNORECASE))
                if not has_hitl_escape:
                    score -= 10
                    suggestions.append("Agent AOD 缺少'人机协同 (HITL) 逃生通道' (低置信度与高危写操作人工审批闭环)")

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

            # 检查是否有三道/四道防线自检
            if file_path.suffix.lower() == ".md":
                has_defenses = bool(re.search(r"(防线|Team Allocation|团队分配|变更隔离)", content, re.IGNORECASE))
                if not has_defenses:
                    score -= 10
                    suggestions.append("CM 缺少防线评审自检表 (团队分配、变更隔离、OM衔接、Agent契约无状态测试)")

            # Agent AI 专属 CM 深度审计 (上下文修剪、语义工具代理、确定性状态机、统一模型网关)
            is_agent_cm = bool(re.search(r"(Agent|智能体|COMP-CTX|COMP-TOOL|COMP-STATE|COMP-GATEWAY|Context Pruning|JSON Schema)", content, re.IGNORECASE))
            if is_agent_cm:
                has_agent_core_comps = bool(re.search(r"(COMP-CTX|COMP-TOOL|COMP-STATE|COMP-GATEWAY|COMP-ROUTER)", content))
                if not has_agent_core_comps:
                    score -= 15
                    suggestions.append("Agent CM 缺少核心认知与隔离中间件组件定义 (COMP-CTX, COMP-TOOL, COMP-STATE, COMP-GATEWAY)")

                has_schema_and_stateless = bool(re.search(r"(JSON Schema|Schema|Pydantic)", content, re.IGNORECASE)) and \
                                           bool(re.search(r"(无状态|Stateless)", content, re.IGNORECASE))
                if not has_schema_and_stateless:
                    score -= 10
                    suggestions.append("Agent CM 缺少'工具强类型 Schema 契约校验'或'编排组件完全无状态 (Stateless)'硬指标")

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

            # Agent AI 专属 OM 深度审计 (代码沙箱隔离区、异构 GPU/CPU 拓扑、逃逸防御与长连接流式测试)
            is_agent_om = bool(re.search(r"(Agent|智能体|Sandbox|沙箱|GPU|H100|vLLM|Firecracker|gVisor|MicroVM|流式|WSS)", content, re.IGNORECASE))
            if is_agent_om:
                has_sandbox_zone = bool(re.search(r"(沙箱隔离|Sandbox Zone|MicroVM|Firecracker|gVisor|安全容器)", content, re.IGNORECASE))
                if not has_sandbox_zone:
                    score -= 15
                    suggestions.append("Agent OM 缺少独立的'动态代码执行沙箱隔离区' (Sandbox Zone: MicroVM/安全容器池，默认断网)")

                has_escape_test = bool(re.search(r"(逃逸|Escape|沙箱销毁|长连接|重连风暴|Cold Start|冷启动)", content, re.IGNORECASE))
                if not has_escape_test:
                    score -= 10
                    suggestions.append("Agent OM 缺少'沙箱逃逸防御测试 (Escape Containment)'或'流式长连接雪崩与冷启动时延评估'")

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

            # Agent AI 专属 ADR 深度审计 (确定性锚点、Prompt 锁定逆转成本、黑盒排障代价、评测基准数据)
            is_agent_adr = bool(re.search(r"(Agent|智能体|LLM|大模型|Prompt|Token|StateGraph|ReAct|MicroVM|推理)", content, re.IGNORECASE))
            if is_agent_adr:
                has_deterministic_anchor = bool(re.search(r"(确定性锚点|Deterministic Anchor|外围.*代码|硬熔断|计数器|状态机守护|自觉性|工程确定性)", content, re.IGNORECASE))
                if not has_deterministic_anchor:
                    score -= 15
                    suggestions.append("Agent ADR 缺少'确定性锚点 (Deterministic Anchor)'原则 (严禁单点信任大模型自觉性，需有外围代码硬约束)")

                has_vendor_neutrality = bool(re.search(r"(锁定|Lock-in|逆转成本|Vendor Neutrality|供应商绑定|网关隔离|迁移成本)", content, re.IGNORECASE))
                if not has_vendor_neutrality:
                    score -= 10
                    suggestions.append("Agent ADR 缺少模型/Prompt 锁定与'逆转成本评估 (Vendor Neutrality Review)'")

                has_debuggability = bool(re.search(r"(可观测|黑盒|排障|Debuggability|Tracing|链路追踪|复盘成本)", content, re.IGNORECASE))
                if not has_debuggability:
                    score -= 10
                    suggestions.append("Agent ADR 负面代价中缺少'可观测性与黑盒排障成本 (Debuggability Impact)'分析")

                has_evals_grounding = bool(re.search(r"(评测基准|Evals|Golden Dataset|Benchmark|测试集)", content, re.IGNORECASE))
                if not has_evals_grounding:
                    score -= 10
                    suggestions.append("Agent ADR 方案对比缺少客观'评测基准数据支撑 (Evals Grounding)'，存在主观定性风险")

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

            # Agent AI 专属 ARC 深度审计 (认知有效性、TTFT流式时延、Token 经济学、黄金评测集与硬断电机制)
            is_agent_arc = bool(re.search(r"(Agent|智能体|LLM|大模型|Cognitive|Token|Prompt 注入|Prompt Cache|TTFT|推理)", content, re.IGNORECASE))
            if is_agent_arc:
                has_cognitive_efficacy = bool(re.search(r"(认知有效性|Cognitive Efficacy|达成率|Completion Rate|TCR|Pass@1|幻觉率|Hallucination)", content, re.IGNORECASE))
                if not has_cognitive_efficacy:
                    score -= 15
                    suggestions.append("Agent ARC 缺少'认知有效性与任务达成度'量化指标 (如 TCR/Pass@1, 事实幻觉率, 任务漂移率)")

                has_ttft_latency = bool(re.search(r"(TTFT|首字|Time to First Token|单步.*时延|单步.*耗时|Per-step)", content, re.IGNORECASE))
                if not has_ttft_latency:
                    score -= 10
                    suggestions.append("Agent ARC 缺少'流式首字时延 (TTFT)'或'单步思考时延 (Per-step Latency)'量化分级")

                has_token_economics = bool(re.search(r"(Token.*经济|Unit Economics|单任务成本|成本上限|Cost per|缓存命中|Prompt Cache)", content, re.IGNORECASE))
                if not has_token_economics:
                    score -= 10
                    suggestions.append("Agent ARC 缺少'Token 经济学与成本控制'约束 (如单任务成本上限, Prompt Cache 命中率)")

                has_evals_dataset = bool(re.search(r"(黄金.*集|Golden Dataset|评测集|Evals|基准测试集|Benchmark Dataset)", content, re.IGNORECASE))
                if not has_evals_dataset:
                    score -= 10
                    suggestions.append("Agent ARC 缺少与具体'黄金评测基准集 (Golden Dataset / Evals Pipeline)'的绑定验收机制")

                has_kill_switch = bool(re.search(r"(断电|Kill-Switch|硬熔断|Max Steps|步数上限|死循环.*熔断)", content, re.IGNORECASE))
                if not has_kill_switch:
                    score -= 10
                    suggestions.append("Agent ARC 缺少失控概率兜底的'硬性断电机制 (The Kill-Switch Metric: 成本上限/Max Steps 熔断)'")

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

            # 如果涉及 Agent / AI 智能体系统，检查自主等级 (LoA) 与人机协作容错回退机制
            is_agent_system = bool(re.search(r"(Agent|智能体|LLM|大模型|AI Coding|推理)", content, re.IGNORECASE))
            if is_agent_system:
                has_loa = bool(re.search(r"(自主等级|Level of Autonomy|LoA|L1|L2|L3|Copilot|Human-in-the-loop|Autonomous)", content, re.IGNORECASE))
                has_fallback = bool(re.search(r"(回退|Fallback|容错底线|人工介入|降级)", content, re.IGNORECASE))
                if not (has_loa and has_fallback):
                    score -= 10
                    suggestions.append("Agent AI 业务目标缺少明确的'自主等级 (Level of Autonomy, LoA: L1/L2/L3)'或'容错底线与回退机制 (Fallback)'")

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

            # 如果涉及 Agent / AI 智能体系统，检查 Token 单位经济学、模型中立性与爆炸半径约束
            is_agent_system = bool(re.search(r"(Agent|智能体|LLM|大模型|AI Coding|推理)", content, re.IGNORECASE))
            if is_agent_system:
                has_token_budget = bool(re.search(r"(Token|成本上限|Hard Cap|预算硬顶|Unit Economics)", content, re.IGNORECASE))
                has_model_agnostic = bool(re.search(r"(模型中立|模型网关|LLM Gateway|Model Agnostic|开源模型)", content, re.IGNORECASE))
                has_blast_radius = bool(re.search(r"(爆炸半径|Blast Radius|沙箱|最小特权|权限隔离)", content, re.IGNORECASE))
                if not (has_token_budget and has_model_agnostic and has_blast_radius):
                    score -= 15
                    suggestions.append("Agent AI 架构约束缺少'Token成本硬顶'、'模型中立性/网关'或'爆炸半径沙箱隔离 (Blast Radius)'硬约束")

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

            # Agent AI 专属深度审计 (若识别为 Agent/AI 范式系统)
            is_agent_context = bool(re.search(r"(Agent|智能体|大模型|LLM|推理网关|Tool Sandbox|Prompt)", content, re.IGNORECASE))
            if is_agent_context:
                # 1. 模型基座显性化与降级兜底检查
                has_model_dep = bool(re.search(r"(模型基座|LLM|Foundation Model|推理网关|模型提供方)", content, re.IGNORECASE))
                if not has_model_dep:
                    score -= 10
                    suggestions.append("Agent 系统上下文未显性标注模型基座提供方 (Foundation Model / LLM Provider) 及其主备降级链路")

                # 2. 受控工具执行沙箱与副作用界限检查
                has_sandbox_or_sideeffect = bool(re.search(r"(沙箱|Sandbox|副作用|Side-effect|只读探查|Read-only Probe)", content, re.IGNORECASE))
                if not has_sandbox_or_sideeffect:
                    score -= 10
                    suggestions.append("Agent 系统上下文缺少受控工具沙箱 (Tool Sandbox) 或未显式标注交互副作用 (只读探查 vs 不可逆副作用)")

                # 3. 人机协同角色分离检查 (发起人 vs 审批人/HITL)
                has_hitl_split = bool(re.search(r"(HITL|人机协同|审批人|仲裁员|Supervisor|Approver|人工介入)", content, re.IGNORECASE))
                if not has_hitl_split:
                    score -= 10
                    suggestions.append("Agent 系统上下文未对自然人进行人机协同角色分离 (缺少专职审批人/仲裁员 Human Approver 或 HITL 兜底回路)")

                # 4. Agent 爆炸半径沙盘检验记录 (Blast Radius Walkthrough)
                has_blast_radius = bool(re.search(r"(爆炸半径|Blast Radius|沙盘|失控指令|429.*限流|Prompt.*注入)", content, re.IGNORECASE))
                if not has_blast_radius:
                    score -= 10
                    suggestions.append("Agent 系统上下文缺少'Agent 爆炸半径沙盘检验记录' (Blast Radius Walkthrough: 恶意失控指令截断与模型宕机降级)")

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

            # Agent AI 专属风格审查 (认知拓扑、快慢思考与死循环防御)
            is_agent_style = bool(re.search(r"(Agent|智能体|ReAct|Reflection|StateGraph|认知循环|快思考|慢思考|Fast-Slow|Supervisor)", content, re.IGNORECASE))
            if is_agent_style:
                has_loop_breaker = bool(re.search(r"(死循环|Loop-Breaker|Max Steps|土拨鼠|强制截断|转人工|HITL)", content, re.IGNORECASE))
                if not has_loop_breaker:
                    score -= 15
                    suggestions.append("Agent 架构风格选型缺少'死循环防御审查' (The Loop-Breaker Test: Max Steps 硬限制与状态机物理强制截断转人工)")

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

            # 检查三步/四步压力测试 (Business Proxy, Lifecycle, CM Driving, Replay)
            has_stress_tests = bool(re.search(r"(压力测试|业务代言人|走查|生命周期完整性|驱动组件模型|Walkthrough)", content, re.IGNORECASE))
            if not has_stress_tests:
                score -= 10
                suggestions.append("CDM 缺少合格性压力测试 (业务走查、生命周期完整性、驱动 CM 验证) 自检记录")

            # Agent AI 专属 CDM 深度审计 (一等公民实体、状态可复现性与重放审计)
            is_agent_cdm = bool(re.search(r"(Agent|智能体|CognitiveSession|ExecutionStep|Thought|Action|Observation|记忆|Token|负向假设)", content, re.IGNORECASE))
            if is_agent_cdm:
                has_first_class_entities = bool(re.search(r"(Session|Turn|Step|Thought|Observation|Action|NegativeHypothesis|负向假设|认知会话|执行步骤)", content, re.IGNORECASE))
                if not has_first_class_entities:
                    score -= 15
                    suggestions.append("Agent CDM 缺少认知轨迹一等公民实体 (Session, Turn, Step, Thought, Action, Observation, NegativeHypothesis)")

                has_replay_walkthrough = bool(re.search(r"(Replay|重放|Time-travel|时间旅行|单步追溯|审计验证)", content, re.IGNORECASE))
                if not has_replay_walkthrough:
                    score -= 10
                    suggestions.append("Agent CDM 缺少'重放与审计'实战验证 (The Replay Walkthrough: 还原历史单步推理与工具调用细节)")

        # 14. Utility Tree & ATAM 场景推演专属规范深度审计 (SEI / IBM 架构权衡分析法标准)
        is_atam_file = "utility-tree" in file_path.name.lower() or "atam" in file_path.name.lower()

        if is_atam_file and file_path.suffix.lower() == ".md":
            # 检查效用树分级结构与二维优先级矩阵定级
            has_utility_matrix = bool(re.search(r"\|.*(效用树|质量属性维度|场景标识|业务重要性|技术实现风险|推演级别).*\|", content, re.IGNORECASE))
            has_priority_ranking = bool(re.search(r"(\(High,\s*High\)|\(H,\s*H\)|重点推演|Priority\s*1)", content, re.IGNORECASE))
            if not (has_utility_matrix and has_priority_ranking):
                score -= 15
                suggestions.append("ATAM 缺少结构化效用树推导矩阵或 (High, High) 二维优先级定级")

            # 检查六要素场景法 (刺激源、刺激、环境、构件、响应、度量)
            has_six_parts = bool(re.search(r"(刺激源|Source)", content, re.IGNORECASE)) and \
                            bool(re.search(r"(刺激|Stimulus)", content, re.IGNORECASE)) and \
                            bool(re.search(r"(环境|Environment)", content, re.IGNORECASE)) and \
                            bool(re.search(r"(构件|Artifact)", content, re.IGNORECASE)) and \
                            bool(re.search(r"(响应|Response)", content, re.IGNORECASE)) and \
                            bool(re.search(r"(度量|Response Measure)", content, re.IGNORECASE))
            if not has_six_parts:
                score -= 20
                suggestions.append("ATAM 场景定义未完整遵循'六要素场景法' (刺激源、刺激、环境、构件、响应、度量)")

            # 检查四大核心推演产出 (敏感点、权衡点、架构风险、无风险项)
            has_sensitivity = bool(re.search(r"(敏感点|Sensitivity\s*Point)", content, re.IGNORECASE))
            has_tradeoff = bool(re.search(r"(权衡点|Trade-off\s*Point)", content, re.IGNORECASE))
            has_risk = bool(re.search(r"(架构风险|风险点|Architectural\s*Risk)", content, re.IGNORECASE))
            has_non_risk = bool(re.search(r"(无风险项|Non-Risk)", content, re.IGNORECASE))

            missing_outputs = []
            if not has_sensitivity: missing_outputs.append("敏感点 (Sensitivity Point)")
            if not has_tradeoff: missing_outputs.append("权衡点 (Trade-off Point)")
            if not has_risk: missing_outputs.append("架构风险 (Risk)")
            if not has_non_risk: missing_outputs.append("无风险项 (Non-Risk)")

            if missing_outputs:
                score -= 20
                suggestions.append(f"ATAM 场景推演缺少核心产出类别: {', '.join(missing_outputs)}")

            # 检查拔线断流沙盘演练
            has_sever_cord = bool(re.search(r"(拔线|断流|Sever the Cord)", content, re.IGNORECASE))
            if not has_sever_cord:
                score -= 10
                suggestions.append("ATAM 缺少'拔线与断流'沙盘极限故障推演记录")

            # 检查风险处置闭环矩阵 (Risk-to-Action: 关联 PoC、新 ADR 或技术债务)
            has_risk_closure = bool(re.search(r"\|.*(风险编号|处置动作|PoC|ADR|闭环状态|Action).*\|", content, re.IGNORECASE))
            if not has_risk_closure:
                score -= 15
                suggestions.append("ATAM 缺少'风险处置闭环追踪矩阵' (所有风险必须强制绑定 PoC、ADR 或技术债务)")

        # 15. Proof of Concept (PoC) 专属规范深度审计 (IBM 架构验证与深水区工程刺破标准)
        is_poc_file = "poc" in file_path.name.lower()

        if is_poc_file and file_path.suffix.lower() == ".md":
            # 检查穿透式垂直切片定位 (Tracer Bullet / Spike)
            has_tracer_bullet = bool(re.search(r"(垂直切片|Tracer\s*Bullet|Spike|极窄深度)", content, re.IGNORECASE))
            if not has_tracer_bullet:
                score -= 15
                suggestions.append("PoC 缺少'穿透式垂直切片 (Tracer Bullet / Spike)'明确声明，需聚焦单一险峻链路剥离常规业务")

            # 检查关联架构推导链路 (关联 ADR, ARC 或承接 ATAM 风险项)
            has_architecture_links = bool(re.search(r"(ADR|架构决策)", content, re.IGNORECASE)) and \
                                     bool(re.search(r"(ARC|NFR|质量属性|需求)", content, re.IGNORECASE))
            if not has_architecture_links:
                score -= 15
                suggestions.append("PoC 未明确关联驱动它的上游架构决策 (ADR) 或架构需求 (ARC/ATAM 风险项)")

            # 检查时间盒与不可篡改的预设熔断指标 (Kill Criteria)
            has_timebox = bool(re.search(r"(时间盒|Time-box|工作日|周期)", content, re.IGNORECASE))
            has_kill_criteria = bool(re.search(r"(熔断指标|Kill\s*Criteria|淘汰指标|失败门槛)", content, re.IGNORECASE))
            if not has_timebox:
                score -= 10
                suggestions.append("PoC 缺少'严格时间盒 (Time-boxing 1~2周)'周期控制")
            if not has_kill_criteria:
                score -= 15
                suggestions.append("PoC 缺少预先设立的不可篡改'熔断指标 (Kill Criteria)'，必须明确何种情况下方案被判定淘汰")

            # 检查破坏性混沌实验与真实压测 (Chaos, 注入, 崩溃, 拟真网络)
            has_destructive_chaos = bool(re.search(r"(破坏性|混沌|Chaos|延迟注入|丢包|kill|崩溃|断流|断电|抖动)", content, re.IGNORECASE))
            if not has_destructive_chaos:
                score -= 15
                suggestions.append("PoC 缺少真实物理条件下的'破坏性混沌实验 (Chaos & True Physics)'，严禁在玩具 localhost 环境走过场")

            # 检查最终结项决议与架构资产 100% 闭环反哺 (更新 CM/OM/ADR)
            has_resolution = bool(re.search(r"(采纳|Accepted|Rejected|淘汰|决议|结项)", content, re.IGNORECASE))
            has_feedback_loop = bool(re.search(r"(闭环|反哺|校准|CM|OM|ADR|Feedback\s*Loop)", content, re.IGNORECASE))
            if not (has_resolution and has_feedback_loop):
                score -= 15
                suggestions.append("PoC 缺少明确的结项最终决议或 100% 架构闭环反哺记录 (必须反哺修改 CM/OM/ADR)")

        # 16. ARB (Architecture Review Board) 评审准入与终审闸口专项深度审计
        is_arb_file = "arb" in file_path.name.lower()

        if is_arb_file and file_path.suffix.lower() == ".md":
            # 检查准入核验门槛与工件完整性 (AOD, CM, OM, CDM, ARC, ADR)
            has_entry_checklist = bool(re.search(r"\|.*(准入|核验门槛|工件|Checklist|Entry).*\|", content, re.IGNORECASE))
            has_core_artifacts = bool(re.search(r"(AOD|概览图)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(CM|组件模型)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(OM|运行模型)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(ARC|架构需求)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(ADR|决策)", content, re.IGNORECASE))
            if not (has_entry_checklist and has_core_artifacts):
                score -= 15
                suggestions.append("ARB 评审缺少'准入检查清单'或未完整涵盖核心架构工件包 (AOD, CM, OM, CDM, ARC, ADR)")

            # 检查跨域横切会签预审 (InfoSec 安全合规与 SRE 运维)
            has_presignoffs = bool(re.search(r"(安全|合规|InfoSec|Compliance)", content, re.IGNORECASE)) and \
                              bool(re.search(r"(运维|SRE|基础设施|Infra)", content, re.IGNORECASE)) and \
                              bool(re.search(r"(会签|预审|Sign-off)", content, re.IGNORECASE))
            if not has_presignoffs:
                score -= 15
                suggestions.append("ARB 评审缺少'信息安全(InfoSec)'与'基础架构(SRE)'跨域会签预审记录")

            # 检查高风险 PoC 验证避险支持
            has_poc_support = bool(re.search(r"(PoC|概念验证|压测|实测)", content, re.IGNORECASE))
            if not has_poc_support:
                score -= 10
                suggestions.append("ARB 评审缺少对高风险技术项的'PoC 实证结项与破坏性实验'背书")

            # 检查 ARB 五维核心评估质询
            has_eval_framework = bool(re.search(r"(业务与价值|Business\s*Fit)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(可行性|NFR|履约)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(权衡|代价|Trade-off)", content, re.IGNORECASE)) and \
                                 bool(re.search(r"(运维|Day-2|生命周期)", content, re.IGNORECASE))
            if not has_eval_framework:
                score -= 15
                suggestions.append("ARB 评审缺少'五维深度评估审查框架' (业务对齐、NFR可行性、标准合规、权衡透明度、Day-2运维)")

            # 检查已知局限与技术债务台账 (Known Limitations & Debt Ledger)
            has_debt_ledger = bool(re.search(r"\|.*(技债编号|技术债务|Known Limitations|债务简述|偿还|Ledger).*\|", content, re.IGNORECASE))
            if not has_debt_ledger:
                score -= 15
                suggestions.append("ARB 评审缺少结构化的'已知局限与技术债务台账 (Known Limitations & Debt Ledger)'")

            # 检查 ARB 四大规范裁决结论与整改行动项
            has_verdict = bool(re.search(r"(Approved|Conditionally\s*Approved|Architecture\s*Exception|Rejected|裁决结论)", content, re.IGNORECASE))
            has_action_items = bool(re.search(r"(行动项|Action\s*Item|整改|复核)", content, re.IGNORECASE))
            if not (has_verdict and has_action_items):
                score -= 15
                suggestions.append("ARB 评审缺少明确的'四大裁决结论之一'或'整改行动项 (Action Items)'与责任期限")

            # Agent AI 专属 ARB 深度审计 (独立评测集盲测、Token 预算模型、物理熔断与一票否决红线)
            is_agent_arb = bool(re.search(r"(Agent|智能体|LLM|大模型|Prompt|Token|沙箱|Evals)", content, re.IGNORECASE))
            if is_agent_arb:
                has_evals_and_budget = bool(re.search(r"(评测基准|Evals|Baseline|黄金测试集|盲测)", content, re.IGNORECASE)) and \
                                       bool(re.search(r"(Token.*预算|Token.*成本|Token Budget Envelope|配额测算)", content, re.IGNORECASE))
                if not has_evals_and_budget:
                    score -= 15
                    suggestions.append("Agent ARB 评审缺少'评测基准报告 (Evals Baseline Suite)'或'Token 成本模型与配额测算表'")

                has_red_flags = bool(re.search(r"(一票否决|Red Flag|裸奔|断电开关|Kill Switch|物理熔断)", content, re.IGNORECASE))
                if not has_red_flags:
                    score -= 10
                    suggestions.append("Agent ARB 评审缺少'一票否决红线核验' (裸奔 Agent、无量化评测、无断电开关 Kill Switch)")

        # 17. Automated Architecture Conformance & Compliance 架构合规扫描专项深度审计
        is_conformance_file = "conformance" in file_path.name.lower() or "compliance" in file_path.name.lower()

        if is_conformance_file and file_path.suffix.lower() == ".md":
            # 检查四大核心扫描维度覆盖 (分层边界、数据所有权、包拓扑规范、供应链安全)
            has_layering = bool(re.search(r"(分层|边界|Layering|ADP|无环)", content, re.IGNORECASE))
            has_data_ownership = bool(re.search(r"(数据所有权|持久化|Data Ownership|私有)", content, re.IGNORECASE))
            has_topology = bool(re.search(r"(包结构|拓扑|契约|Contract|命名|Stereotype)", content, re.IGNORECASE))
            has_supply_chain = bool(re.search(r"(供应链|安全|开源协议|License|CVE|SBOM)", content, re.IGNORECASE))

            missing_dims = []
            if not has_layering: missing_dims.append("分层边界扫描 (Layering & ADP)")
            if not has_data_ownership: missing_dims.append("数据所有权防腐 (Data Ownership)")
            if not has_topology: missing_dims.append("包结构与契约规范 (Package Topology)")
            if not has_supply_chain: missing_dims.append("供应链与开源合规 (Supply Chain & License)")

            if missing_dims:
                score -= 20
                suggestions.append(f"架构合规扫描缺少核心扫描维度: {', '.join(missing_dims)}")

            # 检查 CI/CD 违规即熔断机制 (Break the Build)
            has_break_build = bool(re.search(r"(熔断|Break the Build|中断|禁止合入|PR)", content, re.IGNORECASE))
            if not has_break_build:
                score -= 15
                suggestions.append("架构合规扫描缺少 CI/CD '违规即熔断 (Break the Build)' 强制拦截策略")

            # 检查测试规则与 CM 组件模型 1:1 映射
            has_cm_mapping = bool(re.search(r"(CM-\d+|COMP-\d+|组件模型|映射|契约编号)", content, re.IGNORECASE))
            if not has_cm_mapping:
                score -= 15
                suggestions.append("架构测试规则未与组件模型 (CM-00X / COMP-XXX) 建立 1:1 追溯映射")

            # 检查架构单元测试代码化用例 (ArchUnit / 架构即代码实现)
            has_code_example = bool(re.search(r"(ArchTest|ArchRule|ArchUnit|@Test|classes|layeredArchitecture|assert|ast\.)", content, re.IGNORECASE))
            if not has_code_example:
                score -= 15
                suggestions.append("缺少'架构即测试 (Architecture as Tests)'代码化单元测试实录用例")

            # 检查架构特例豁免带有时效 (Architecture Exception with Expire Date)
            has_exceptions_with_expiry = bool(re.search(r"\|.*(豁免|特例|Exception).*\|", content, re.IGNORECASE)) and \
                                         bool(re.search(r"(到期|失效|Expire|202\d-\d{2}-\d{2})", content, re.IGNORECASE))
            if not has_exceptions_with_expiry:
                score -= 15
                suggestions.append("缺少纳管的'架构特例豁免 (Architecture Exception)'台账或未配置明确的到期失效日 (Expire Date)")

            # 检查基线冻结与渐进式治理策略 (Freezing Baseline)
            has_baseline_freezing = bool(re.search(r"(基线|冻结|Baseline|存量|增量)", content, re.IGNORECASE))
            if not has_baseline_freezing:
                score -= 10
                suggestions.append("缺少面对存量系统的'基线冻结与增量零容忍'治理策略")

            # Agent AI 专属合规扫描深度审计 (Tool Schema 强校验、Prompt 持续评测门禁、网关收敛防线)
            is_agent_conformance = bool(re.search(r"(Agent|智能体|LLM|Tool|Schema|Prompt|Fuzzing|Guardrail)", content, re.IGNORECASE))
            if is_agent_conformance:
                has_tool_and_gateway = bool(re.search(r"(Tool.*Schema|强类型|Pydantic|网关收敛|LLM.*Gateway)", content, re.IGNORECASE))
                if not has_tool_and_gateway:
                    score -= 15
                    suggestions.append("Agent 合规扫描缺少'Tool Schema 强类型校验'或'业务代码禁直连大模型 SDK 网关收敛防线'")

                has_evals_and_fuzzing = bool(re.search(r"(Continuous Evals|持续评测|Smoke Evals|TCR.*衰减|Fuzzing|越狱|模糊测试)", content, re.IGNORECASE))
                if not has_evals_and_fuzzing:
                    score -= 10
                    suggestions.append("Agent 合规扫描缺少'CI 持续评测门禁 (Continuous Evals)'或'对抗性安全模糊测试 (Fuzzing)'")

        # 18. Technical Debt Ledger (技术债务台账与治理) 专属规范深度审计
        is_debt_file = "technical-debt" in file_path.name.lower() or "debt-ledger" in file_path.name.lower()

        if is_debt_file and file_path.suffix.lower() == ".md":
            # 检查债务分类与定级体系 (架构型、代码型、基础设施型、文档型)
            has_taxonomy = bool(re.search(r"(架构型|Architectural\s*Debt)", content, re.IGNORECASE)) and \
                           bool(re.search(r"(代码|设计|Code|Design)", content, re.IGNORECASE)) and \
                           bool(re.search(r"(基础设施|运维|Infrastructure|Operational)", content, re.IGNORECASE))
            if not has_taxonomy:
                score -= 15
                suggestions.append("技术债务台账缺少严谨的'债务分类与定级体系' (架构型债务、代码设计型、基础设施型)")

            # 检查'本金'与'利息'量化双重度量机制 (Principal vs Interest)
            has_principal = bool(re.search(r"(本金|Principal|人天|工时|重构成本)", content, re.IGNORECASE))
            has_interest = bool(re.search(r"(利息|Interest|摩擦成本|系统风险|代价)", content, re.IGNORECASE))
            if not (has_principal and has_interest):
                score -= 20
                suggestions.append("技术债务缺少'本金(重构人天)'与'利息(摩擦成本与系统风险)'量化双重度量")

            # 检查关联架构资产回溯 (CM, OM, ADR, ARB Exemption)
            has_arch_links = bool(re.search(r"(CM|OM|ADR|ARB|COMP-|组件|决策|豁免)", content, re.IGNORECASE))
            if not has_arch_links:
                score -= 15
                suggestions.append("技术债务条目未明确关联上游架构资产 (CM组件、OM部署、ADR决策或ARB豁免)")

            # 检查偿还契约、截止到期日与责任人 (Repayment Contract & Due Date)
            has_repayment = bool(re.search(r"(偿还|Repayment|清偿|计划)", content, re.IGNORECASE)) and \
                             bool(re.search(r"(截止|到期|Due\s*Date|期限|Sprint|202\d-\d{2}-\d{2})", content, re.IGNORECASE)) and \
                             bool(re.search(r"(责任人|Owner|批准人)", content, re.IGNORECASE))
            if not has_repayment:
                score -= 15
                suggestions.append("技术债务缺少明确的'偿还契约' (承接责任人、批准人与具体截止到期日/Sprint)")

            # 检查偿债预算硬性配额机制 (Debt Budget 15%~20%)
            has_budget = bool(re.search(r"(预算|Budget|15%|20%|Story\s*Points|产能配额)", content, re.IGNORECASE))
            if not has_budget:
                score -= 15
                suggestions.append("技术债务治理缺少硬性的'迭代偿还预算配额' (每个敏捷冲刺切出 15%~20% 产能)")

            # 检查状态机与生命周期流转 (Active, Repaid, Accepted)
            has_status_lifecycle = bool(re.search(r"(Active|Repaid|Accepted|挂账|已偿还|接受风险|核销)", content, re.IGNORECASE))
            if not has_status_lifecycle:
                score -= 10
                suggestions.append("技术债务台账缺少规范的状态流转字段 (Active / Repaid / Accepted)")

            # Agent AI 专属认知技术债务审计 (提示词打补丁、上下文未修剪、专有模型锁定、评测滞后)
            is_agent_debt = bool(re.search(r"(Agent|智能体|LLM|Prompt|Token|上下文|模型锁定|Evals)", content, re.IGNORECASE))
            if is_agent_debt:
                has_cognitive_debts = bool(re.search(r"(提示词打补丁|Prompt-Patching|上下文.*修剪|Context Bloat|模型锁定|Model Lock-in|评测滞后|Evaluation Debt)", content, re.IGNORECASE))
                if not has_cognitive_debts:
                    score -= 15
                    suggestions.append("Agent 技债台账缺少专属认知债务识别 (如提示词打补丁债务、上下文未修剪债务、模型锁定债务、评测滞后债务)")

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
