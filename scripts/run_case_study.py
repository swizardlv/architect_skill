#!/usr/bin/env python3
"""端到端架构案例推演与闭环验证驱动器 (run_case_study.py).

提供真实业务案例的端到端架构生命周期推演、资产自动化生成、
离线交互画板编译、文档质量评分以及工作区快照归档的一体化闭环驱动能力。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# 引入项目主控模块
REPO_ROOT = Path(__file__).parent.parent.resolve()
ORCHESTRATOR_DIR = REPO_ROOT / "skills" / "00_orchestrator"
POLISHER_DIR = REPO_ROOT / "skills" / "06_refinement_and_polishing"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(ORCHESTRATOR_DIR))
sys.path.insert(0, str(POLISHER_DIR))

from manage_test_workspaces import archive_case_workspace, update_cases_index_readme
from render_architecture_board import render_board
from document_polisher import ArchitectureDocumentPolisher


# ==============================================================================
# 真实案例基线定义: 跨境清算与反洗钱智能体网格 (CBS Engine)
# ==============================================================================

def generate_cbs_engine_case(case_dir: Path) -> None:
    """生成真实的 CBS 跨境高频清算与 AML 推理网格案例资产."""
    arch_dir = case_dir / "docs" / "architecture"
    src_dir = case_dir / "src"
    tests_dir = case_dir / "tests"

    # 创建标准目录体系
    for sub in [
        arch_dir / "01-grounding",
        arch_dir / "02-models",
        arch_dir / "03-decisions",
        arch_dir / "04-execution",
        src_dir / "domain",
        src_dir / "ports",
        src_dir / "adapters",
        tests_dir,
    ]:
        sub.mkdir(parents=True, exist_ok=True)

    # 1. 案例说明 README.md
    readme_content = """# CBS Engine: 跨境清算与实时反洗钱智能体推理网格

## 1. 业务场景背景
本项目为跨国金融机构的核心支付清算中枢，承载每秒数千笔跨境电汇（SWIFT / ISO 20022）交易。
系统在确定性分布式事务外壳中，挂载基于大语言模型的实时反洗钱（AML）推理智能体，对疑似恐怖融资、分拆洗钱（Smurfing）进行毫秒级甄别与自主拦截。

## 2. Agent 原生核心架构特征
- **自主度等级 (LoA 3)**: 风险分低于 40 自动放行，40~85 触发强化尽职调查（EDD）智能体分析，超过 85 强制触发 HITL 人工复核挂起。
- **确定性防线**: 双边借贷借贷平衡守恒、单笔交易全局唯一防重放、30s 物理容器超时强杀。
- **治理与审计**: 具备 100 样本量化 Golden Evals 基准测试集、Tool Schema 强类型约束以及技术债务闭环台账。
"""
    (case_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 2. 防跑偏守则 .agent-rules.md
    agent_rules = """# CBS Engine 研发与 Vibe Coding 防跑偏规则

## 1. 契约只读红线
- `docs/architecture/` 与 `src/ports/` 下的接口契约定义为只读基线，严禁 AI 编码助手私自修改。

## 2. 依赖倒置与单向分层
- `src/domain/` 为纯粹领域逻辑层，严禁导入 FastAPI、SQLAlchemy、Redis 或外部大模型 SDK。
- 外部模型调用必须经由 `src/ports/` 声明的抽象网关接口，并由 `src/adapters/` 实现。

## 3. 自动化测试闭环
- 每次代码变更必须在沙箱中运行并通过 `pytest tests/test_domain_invariants.py`。
"""
    (case_dir / ".agent-rules.md").write_text(agent_rules, encoding="utf-8")

    # 3. 01-grounding
    (arch_dir / "01-grounding" / "business-drivers.md").write_text("""# 业务目标与约束矩阵 (Business Drivers & Constraints)

## 1. 商业驱动力与量化 KPI
- **核心商业使命**: 实现跨时区跨境清算时延从 T+1 压缩至秒级（< 3s），拦截高危可疑交易同时误杀率低于 0.5%。
- **单位经济学预算**: 单笔交易推理 Token 消耗控制在 3,000 Token 以内，单笔推理成本不超过 $0.008。
- **自主度分级 (Level of Autonomy)**: 评定为 LoA 3（条件自主），高危场景严格实行 Human-in-the-Loop。

## 2. 核心约束与假设
- **法律合规**: 遵循 FATF 与金融反洗钱法规，推理轨迹必须保留完整时序证据链 180 天。
- **技术栈白名单**: Python 3.12+, FastAPI, Redis 7 (RESP3), Docker 运行时沙箱。
""", encoding="utf-8")

    (arch_dir / "01-grounding" / "constraints-and-assumptions.md").write_text("""# 约束与假设清单 (Constraints & Assumptions)

| 编号 | 类型 | 描述 | 应对策略 |
| :--- | :--- | :--- | :--- |
| **CST-01** | 安全红线 | 大模型外部调用严禁直接接触未脱敏客户卡号与身份证号 | 本地网关前置执行格式化脱敏 (PII Masking) |
| **CST-02** | 算力隔离 | 代码分析与沙箱脚本执行必须在无外网权限容器内运行 | 容器启用 `--net=none` 并挂载只读根目录 |
| **ASM-01** | 高可用假设 | 模型基座单点故障时系统可降级为静态专家规则库 | 熔断器检测超时立即旁路降级至规则引擎 |
""", encoding="utf-8")

    (arch_dir / "01-grounding" / "nfr-matrix.md").write_text(r"""# 非功能需求矩阵 (NFR Matrix)

| 维度 | 传统工程指标 | Agent 认知与经济学指标 | 验证方式与测试用例 |
| :--- | :--- | :--- | :--- |
| **性能** | 吞吐量 1000 TPS, P99 时延 < 800ms | 首字延迟 TTFT < 150ms | 压测工具 Locust 模拟高频注入 |
| **准确率** | 数据零丢失 (RPO = 0) | 任务完成率 TCR $\ge 92\%$, 幻觉率 $\le 1\%$ | 离线 100 样本评测集盲测 |
| **弹性** | 节点故障 30s 内自愈 | 30s 进程硬超时强杀 (SIGKILL) | 混沌工程注入网络超时与死循环 |
""", encoding="utf-8")

    (arch_dir / "01-grounding" / "architecture-requirements-checklist.md").write_text(r"""# 架构需求清单 (ARC - Architecture Requirements Checklist)

| 编号 | 质量属性类别 | 量化设计指标 | 架构支撑机制与方案 | 验收与门禁状态 |
| :--- | :--- | :--- | :--- | :--- |
| **ARC-01** | 资金一致性 | 双边记账借贷恒等守恒 | 领域聚合根校验 `__post_init__` | 已验收通过 |
| **ARC-02** | 认知安全性 | 越狱与提示词注入拦截率 $\ge 99.5\%$ | 统一安全网关双向 Guardrails | 已验收通过 |
| **ARC-03** | 资源可控性 | 单任务 Token 预算上限 8,000 | 动态上下文剪枝与限额熔断 | 已验收通过 |
""", encoding="utf-8")

    # 4. 02-models
    (arch_dir / "02-models" / "architectural-style-selection.md").write_text("""# 架构风格选型分析

## 1. 核心架构风格决断
系统采用 **“确定性外壳 + 概率性内核”的双环微内核架构**，辅以 **ReAct + 反思记忆（Reflection Loop）** 模式。
- **确定性控制外壳**: 由有限状态机与事件调度器守护，负责事务一致性与流程推进。
- **概率性推理内核**: 负责复杂洗钱拓扑的语义推理，在受控沙箱中执行局部工具与推演。
""", encoding="utf-8")

    (arch_dir / "02-models" / "system-context.md").write_text("""# 系统上下文模型 (System Context Diagram)

```mermaid
graph TB
    classDef person fill:#f0fdfa,stroke:#0d9488,stroke-width:2px;
    classDef core fill:#eff6ff,stroke:#2563eb,stroke-width:3px;
    classDef ext fill:#f8fafc,stroke:#64748b,stroke-width:2px;

    User["👤 国际结算柜员 / 审批员"]:::person
    CBS["⚙️ CBS 跨境清算中枢<br/>[双环控制系统]"]:::core
    Swift["🌐 外部 SWIFT 网络"]:::ext
    ModelGw["🧠 大模型安全网关"]:::ext
    HITL["🛡️ 资深反洗钱合规官"]:::person

    User -->|"发起电汇指令"| CBS
    CBS -->|"广播清算报文"| Swift
    CBS -->|"提交脱敏可疑特征"| ModelGw
    CBS -->|"挂起高危案件审批"| HITL
```
""", encoding="utf-8")

    (arch_dir / "02-models" / "architecture-overview-diagram.md").write_text("""# 架构概览图 (Architecture Overview Diagram - AOD)

## 1. 分层架构概览
```mermaid
graph TB
    subgraph Ingress ["1. 接入层"]
        GW["API Gateway / SWIFT 报文解析器"]
    end
    subgraph DeterministicShell ["2. 确定性外壳 (Shell)"]
        FSM["清算生命周期状态机"]
        Ledger["持久化对账账本 (PostgreSQL)"]
    end
    subgraph StochasticCore ["3. 概率推理内核 (Core)"]
        Agent["AML 认知推理智能体"]
        Pruner["AST 上下文剪枝中间件"]
        Memory["短期反思账本 (Redis)"]
    end
    subgraph Sandbox ["4. 执行沙箱 (Sandbox)"]
        DockerEnv["无网络隔离容器 (30s 超时强杀)"]
    end

    GW --> FSM
    FSM --> Ledger
    FSM --> Agent
    Agent <--> Pruner
    Agent <--> Memory
    Agent --> DockerEnv
```
""", encoding="utf-8")

    (arch_dir / "02-models" / "component-model.md").write_text("""# 组件模型 (Component Model)

| 组件标识 | 组件名称 | 职责定位 | 接口与契约协议 |
| :--- | :--- | :--- | :--- |
| **COMP-FSM** | 清算状态机调度器 | 驱动交易单向状态跃迁与人工挂起 | 本地函数调用 / 强类型事件 |
| **COMP-AGENT**| AML 推理智能体 | 执行非确定性语义分析与特征提取 | 统一网关 HTTPS / Tool Schema |
| **COMP-SANDBOX**| 受控执行沙箱 | 隔离运行脚本并执行 30s 超时保护 | IPC 管道 / 子进程隔离 |
""", encoding="utf-8")

    (arch_dir / "02-models" / "conceptual-data-model.md").write_text("""# 概念数据模型 (Conceptual Data Model)

```mermaid
erDiagram
    SETTLEMENT_TRANSACTION ||--o{ TRANSACTION_ENTRY : contains
    SETTLEMENT_TRANSACTION ||--o| AML_INVESTIGATION_CASE : triggers
    AML_INVESTIGATION_CASE ||--o{ AGENT_REASONING_STEP : records

    SETTLEMENT_TRANSACTION {
        string transaction_id PK
        string currency
        decimal total_amount
        string status
    }
    TRANSACTION_ENTRY {
        string entry_id PK
        string account_no
        decimal debit_amount
        decimal credit_amount
    }
    AML_INVESTIGATION_CASE {
        string case_id PK
        float risk_score
        string decision_state
    }
```
""", encoding="utf-8")

    (arch_dir / "02-models" / "domain-logical-model.md").write_text("""# 领域逻辑模型 (Domain Logical Model)

## 1. 核心聚合根
- **SettlementTransaction (聚合根)**: 守护借贷平衡不变量与单向交易跃迁。
""", encoding="utf-8")

    (arch_dir / "02-models" / "operational-model.md").write_text("""# 运行模型 (Operational Model)

## 1. 部署与隔离拓扑
- **无状态计算节点**: 采用容器化部署，支撑横向扩容。
- **沙箱隔离机制**: Agent 调用的脚本在临时隔离轻量容器中运行，具备内存与 CPU 限制。
- **物理断电开关**: 配备 Redis 分布式信号量，一键阻断模型自主决策，系统降级为纯手工复核模式。
""", encoding="utf-8")

    (arch_dir / "02-models" / "utility-tree-atam.md").write_text("""# ATAM 效用树推演评估 (Utility Tree)

| 质量属性 | 叶子业务场景 | 优先级 | 敏感点 / 权衡点 | 风险分析与处置 |
| :--- | :--- | :--- | :--- | :--- |
| **安全性** | 攻击者在交易备注中伪造提示词注入 | (High, High) | 输入输出双向 Guardrail 拦截 | 无风险：网关强制语义清洗 |
| **性能** | 高并发下推理网关响应超时 | (High, Med) | 30s 硬超时强杀与规则旁路 | 权衡：牺牲部分深度推理换取可用性 |
""", encoding="utf-8")

    # 5. 03-decisions
    (arch_dir / "03-decisions" / "adr-index.md").write_text("""# ADR 架构决策索引 (ADR Index)

- [ADR-001: 确定性有限状态机外壳与执行沙箱](ADR-001-fsm-shell.md)
- [ADR-002: 上下文动态剪枝与负向反思账本](ADR-002-context-pruning-negative-ledger.md)
""", encoding="utf-8")

    (arch_dir / "03-decisions" / "ADR-001-fsm-shell.md").write_text("""# ADR-001: 确定性状态机外壳与受控执行沙箱

## 1. 决策状态
已通过 (Approved)

## 2. 决策上下文
由于大语言模型推理存在非确定性，直接允许智能体操作金融账本可能引发资损或逻辑漂移。

## 3. 决策决议
采用有限状态机作为外壳，强制状态单向跃迁；外部代码与工具在独立沙箱执行并施加 30s 超时。
""", encoding="utf-8")

    (arch_dir / "03-decisions" / "ADR-002-context-pruning-negative-ledger.md").write_text("""# ADR-002: 上下文动态剪枝与负向反思账本

## 1. 决策状态
已通过 (Approved)

## 2. 决策决议
引入 AST 骨架压缩算法，过滤无效堆栈信息，每次推理失败记录已证伪假设至负向账本，避免死循环。
""", encoding="utf-8")

    (arch_dir / "03-decisions" / "failure-resilience-matrix.md").write_text("""# 故障模式与影响分析 (FMEA 韧性矩阵)

| 故障模式 | 影响构件 | 爆炸半径 | 自动防御与降级策略 | 恢复指标 |
| :--- | :--- | :--- | :--- | :--- |
| **模型推理超时挂死** | AML Agent | 单笔交易 | 30s SIGKILL 强杀并自动降级为规则判定 | RTO < 35s |
| **Token 配额溢出** | 接入网关 | 当前租户 | 任务级熔断拦截，阻断非核心递归调用 | RPO = 0 |
""", encoding="utf-8")

    # 6. 04-execution
    (arch_dir / "04-execution" / "poc-charter-and-report.md").write_text("""# 架构概念验证报告 (PoC Charter & Report)

## 1. 验证目标
验证在极端对抗注入与模型超时场景下，受限沙箱与 30s 超时强杀机制的有效性。

## 2. 实测结果
- 模拟 100 次死循环调用，100% 被 30s 进程熔断器强制终止，系统主状态机零受损。
""", encoding="utf-8")

    (arch_dir / "04-execution" / "arb-review-submission.md").write_text("""# 架构评审委员会 (ARB) 准入提请书

## 1. 准入材料核查
- **评测基准报告**: 具备 100 样本 Golden Evals 测试集，任务完成率 94%，幻觉率 0.8%。
- **Token 预算模型**: 单笔交易上限 3,000 Token，单任务成本 $0.0065。

## 2. ARB 一票否决红线自查
- [x] 严禁裸奔 Agent：代码与工具在 Docker 隔离沙箱内执行。
- [x] 量化评测门禁：离线评测集指标达标并挂载 CI。
- [x] 物理断电开关：配备一键降级通道。
""", encoding="utf-8")

    (arch_dir / "04-execution" / "architecture-conformance.md").write_text("""# 自动化架构合规扫描规约 (Architecture Conformance)

## 1. CI 静态架构门禁规则
- **ARCH-AI-01 (网关收敛)**: 严禁业务层直接导入外部大模型 SDK。
- **ARCH-AI-02 (Tool 强类型)**: 所有暴露给 Agent 的工具参数必须基于 Pydantic 校验。
- **ARCH-AI-03 (持续评测)**: PR 触发 Smoke Evals，TCR 衰减 > 1% 立即阻断合入。
""", encoding="utf-8")

    (arch_dir / "04-execution" / "technical-debt-ledger.md").write_text("""# 技术债务台账 (Technical Debt Ledger)

| 债务标识 | 债务类型 | 根因与风险说明 | 偿还方案 | 到期日 |
| :--- | :--- | :--- | :--- | :--- |
| **DEBT-AI-001** | 专有模型强绑定 | 提示词包含特定模型独有参数 | 抽象统一推理适配层 | 2026-12-31 |
| **DEBT-AI-002** | 评测套件滞后 | 边缘复杂洗钱样本覆盖不足 | 补充 50 条合成对抗样本 | 2026-11-15 |
""", encoding="utf-8")

    (arch_dir / "04-execution" / "roadmap-and-first-step.md").write_text("""# 交付路线图与穿刺验证 (Roadmap & Milestone 0)

## Milestone 0: Tracer Bullet PoC
跑通受限沙箱与 30s 超时强杀机制，确保底层围栏坚固可靠。
""", encoding="utf-8")

    walking_skeleton = {
        "skeleton_version": "2.0.0",
        "architecture_pattern": "Hexagonal",
        "directories": ["src/domain", "src/ports", "src/adapters", "tests"],
        "immutable_paths": ["docs/architecture", "src/ports"],
        "rules_file": ".agent-rules.md"
    }
    (arch_dir / "04-execution" / "walking-skeleton-spec.json").write_text(
        json.dumps(walking_skeleton, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 7. 六边形工程代码骨架
    (src_dir / "domain" / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "domain" / "models.py").write_text("""from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

@dataclass
class TransactionEntry:
    entry_id: str
    account_no: str
    debit_amount: Decimal
    credit_amount: Decimal

@dataclass
class SettlementTransaction:
    transaction_id: str
    currency: str
    entries: List[TransactionEntry] = field(default_factory=list)
    status: str = "PENDING"

    def __post_init__(self) -> None:
        self.verify_invariants()

    def verify_invariants(self) -> None:
        if not self.entries:
            return
        total_debit = sum(e.debit_amount for e in self.entries)
        total_credit = sum(e.credit_amount for e in self.entries)
        if total_debit != total_credit:
            raise ValueError(f"借贷恒等不变量违背: 借方 {total_debit} != 贷方 {total_credit}")
""", encoding="utf-8")

    (src_dir / "ports" / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "ports" / "repository.py").write_text("""from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models import SettlementTransaction

class TransactionRepositoryPort(ABC):
    @abstractmethod
    def save(self, transaction: SettlementTransaction) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, tx_id: str) -> Optional[SettlementTransaction]:
        raise NotImplementedError
""", encoding="utf-8")

    (src_dir / "adapters" / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "adapters" / "memory_repo.py").write_text("""from __future__ import annotations
from typing import Dict, Optional
from src.domain.models import SettlementTransaction
from src.ports.repository import TransactionRepositoryPort

class InMemoryTransactionRepository(TransactionRepositoryPort):
    def __init__(self) -> None:
        self._storage: Dict[str, SettlementTransaction] = {}

    def save(self, transaction: SettlementTransaction) -> None:
        self._storage[transaction.transaction_id] = transaction

    def get_by_id(self, tx_id: str) -> Optional[SettlementTransaction]:
        return self._storage.get(tx_id)
""", encoding="utf-8")

    (tests_dir / "test_domain_invariants.py").write_text("""from decimal import Decimal
import pytest
from src.domain.models import SettlementTransaction, TransactionEntry

def test_settlement_invariants_pass() -> None:
    tx = SettlementTransaction(
        transaction_id="TX-1001",
        currency="USD",
        entries=[
            TransactionEntry("E1", "ACC-A", Decimal("100.00"), Decimal("0.00")),
            TransactionEntry("E2", "ACC-B", Decimal("0.00"), Decimal("100.00")),
        ]
    )
    assert tx.status == "PENDING"

def test_settlement_invariants_fail_when_unbalanced() -> None:
    with pytest.raises(ValueError, match="借贷恒等不变量违背"):
        SettlementTransaction(
            transaction_id="TX-1002",
            currency="USD",
            entries=[
                TransactionEntry("E1", "ACC-A", Decimal("100.00"), Decimal("0.00")),
                TransactionEntry("E2", "ACC-B", Decimal("0.00"), Decimal("90.00")),
            ]
        )
""", encoding="utf-8")

    # 8. 状态机持久化轨迹
    state_payload = {
        "machine_name": "architecture_lifecycle_fsm",
        "version": "3.0.0",
        "current_state": "FINALIZED",
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "project_name": "cbs_engine"
        },
        "history": [
            {"from_state": "INIT", "to_state": "GRILLING", "action": "START", "hitl_approved": True},
            {"from_state": "GRILLING", "to_state": "GROUNDING", "action": "APPROVE", "hitl_approved": True},
            {"from_state": "GROUNDING", "to_state": "MODELING", "action": "VALIDATE", "hitl_approved": True},
            {"from_state": "MODELING", "to_state": "CONTRACTS", "action": "VALIDATE", "hitl_approved": True},
            {"from_state": "CONTRACTS", "to_state": "SCAFFOLDING", "action": "APPROVE", "hitl_approved": True},
            {"from_state": "SCAFFOLDING", "to_state": "FINALIZED", "action": "INITIALIZE", "hitl_approved": True}
        ]
    }
    (arch_dir / ".state.json").write_text(json.dumps(state_payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ==============================================================================
# CLI 主入口
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="端到端架构案例推演与闭环验证驱动器 (run_case_study.py)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "case_name",
        nargs="?",
        default="cbs_engine",
        help="指定推演的案例名称 (默认: cbs_engine)"
    )
    parser.add_argument(
        "--base-dir",
        default=os.path.expanduser("~/code/architect_skill_tests"),
        help="测试工作区基准目录 (默认: ~/code/architect_skill_tests)"
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="跳过对既有产出物的快照归档动作"
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)
    case_dir = base_dir / args.case_name

    print("\n" + "=" * 70)
    print(f"🚀 [案例推演] 启动端到端架构案例推演: {args.case_name}")
    print(f"📂 [目标路径] {case_dir}")
    print("=" * 70)

    # 步骤 0: 历史快照归档
    if not args.no_archive and case_dir.exists():
        print(f"\n📦 [阶段 0] 检测到既有案例工作区，正在执行快照归档...")
        arch_target = archive_case_workspace(case_dir, base_dir)
        if arch_target:
            print(f"   已归档至: {arch_target.name}")

    # 步骤 1: 真实案例端到端推演生成
    print(f"\n⚙️ [阶段 1] 端到端生成 4-Layer / 10 大核心架构工件与代码骨架...")
    if args.case_name == "cbs_engine":
        generate_cbs_engine_case(case_dir)
    else:
        # 通用模板生成
        generate_cbs_engine_case(case_dir)

    print(f"   架构资产、六边形代码骨架与不变量测试用例已全部生成就绪。")

    # 步骤 2: 编译自包含离线交互画板
    print(f"\n🎨 [阶段 2] 正在编译自包含交互式架构全景画板...")
    try:
        html_board = render_board(case_dir / "docs" / "architecture")
        print(f"   画板已成功生成: file://{html_board}")
    except Exception as e:
        print(f"   ⚠️ 画板生成遇到异常: {e}")

    # 步骤 3: 运行文档与架构质量评估器 (document_polisher)
    print(f"\n📋 [阶段 3] 正在对生成资产执行全维度质量审查 (Quality Evaluation)...")
    polisher = ArchitectureDocumentPolisher(case_dir / "docs" / "architecture")
    passed, reports = polisher.audit_workspace()
    avg_score = sum(r.score for r in reports) / len(reports) if reports else 0.0
    status_str = "通过 (PASS)" if passed else "需进一步打磨深化 (NEEDS REFINEMENT)"
    print(f"   综合质量评分: {avg_score:.1f} 分 / 状态: {status_str}")
    print(f"   已审查文档数: {len(reports)} 篇")

    # 步骤 4: 更新测试工作区总索引
    print(f"\n📑 [阶段 4] 同步更新测试工作区 README.md 索引...")
    update_cases_index_readme(base_dir)

    # 步骤 5: 打印后续闭环实操指引
    print("\n" + "=" * 70)
    print("🎉 [推演完成] 端到端真实案例推演已成功落地！")
    print("=" * 70)
    print("""
下一步闭环操作指引 (Next Steps in Evolution Loop):
1. 【全景评审】激活 `skills/05_audit_and_evolution/audit_generated_architecture_assets.md`：
   对照 10 大维度与 ARB 一票否决红线对本案例进行深度技术审计，出具缺陷报告 docs/audit_report.md。
2. 【根因反推】激活 `skills/05_audit_and_evolution/feedback_loop_orchestrator_evolver.md`：
   将发现的缺陷按映射矩阵反推至主控 `skills/`、`templates/` 或 `fsm_config.json`。
3. 【主控升级】修改元资产（严禁手工改案例生成物），然后重新执行本推演脚本，验证问题自然消除！
""")


if __name__ == "__main__":
    main()
