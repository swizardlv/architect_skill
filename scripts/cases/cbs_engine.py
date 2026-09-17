"""案例 1: 跨境金融清算与反洗钱推理系统 (CBS-Engine)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / 'skills' / '00_orchestrator'))

from orchestrate_architecture_lifecycle import ArchitectureLifecycleFSM
from render_architecture_board import render_board

def run_cbs_case_study(target_root: Path) -> None:
    """执行跨境金融清算系统 (CBS-Engine) 架构全流程推演."""
    ws_root = target_root / "docs" / "architecture"
    ws_root.mkdir(parents=True, exist_ok=True)

    print(f"\n======================================================================")
    print(f" 🚀 启动案例推演: 跨境清算与 AML 智能引擎 (CBS-Engine)")
    print(f" 🎯 目标工作区: {ws_root}")
    print(f"======================================================================\n")

    # 1. 初始化状态机
    fsm = ArchitectureLifecycleFSM(workspace_root=ws_root)
    # 若存在历史先重置
    if fsm.state_file.exists():
        fsm.state_file.unlink()
    fsm.resume_or_init()
    print(f"[阶段 0] 初始化完成，当前状态: {fsm.current_state.value}")

    # 2. INIT -> GRILLING
    fsm.advance()
    print(f"[阶段 1] 推进至需求深挖状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 1: grill_architecture_requirements 执行产出
    # -------------------------------------------------------------
    grounding_spec = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "status": "COMPLETED",
        "grounding_spec": {
            "project_name": "cbs-engine-clearing-mesh",
            "business_driver": "解决跨境多币种结算报文歧义挂账率高（日均3%挂账）、洗钱多跳规避识别难的问题。通过确定性记账外壳杜绝资金错配，通过概率智能体内核辅助报文修复与AML推理，单日减少挂账损失超 200 万元。",
            "core_invariants": [
                "借贷记账恒等法则：所有会计分录借贷双方金额绝对守恒，任何时刻账户余额不可为负",
                "清算状态单向流转法则：状态只能沿 PENDING -> VALIDATED -> CLEARED 单向跃迁，禁止状态倒流",
                "资金副作用隔离法则：智能体仅具备只读分析与沙箱仿真修复建议权，严禁直接触发实际资金划扣"
            ],
            "nfr_targets": {
                "throughput_qps": "清算峰值 3000 TPS，平均 800 TPS",
                "p99_latency": "实时记账链路 P99 < 150ms，复杂智能体报文推理 P95 < 2.5s",
                "rpo_rto": "RPO = 0 (零丢失窗口)，RTO < 2 分钟 (双机房热备自愈)",
                "consistency_preference": "CP (强一致优先，网络分区时拒绝入账并进入核算挂起，严禁脏写)",
                "resource_budget": "单任务报文修复 Token 消耗上限 <= 4,000；日均 Token 成本红线设为 500 美元"
            },
            "constraints": {
                "tech_stack_allowlist": ["Python 3.11+", "Go 1.22+", "PostgreSQL 16", "Redis 7", "gRPC"],
                "ops_and_infrastructure": "金融专有内网私有化 K8s 集群，外网完全物理隔离，模型推理经专线内网网关",
                "legacy_integrations": ["SWIFT Alliance Gateway (ISO 20022 / MT 报文)", "银行前置记账核心 (REST/gRPC)", "反洗钱名单黑名单库 (每日离线增量)"]
            },
            "anti_goals": [
                "本期不实现自动向央行发起无人工复核的跨境大额汇款操作",
                "严禁允许智能体自主修改会计科目表与清算汇率参数"
            ]
        }
    }
    (ws_root / "00-grounding" / "grounding-spec.json").write_text(
        json.dumps(grounding_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(" -> 产出资产: 00-grounding/grounding-spec.json 就绪")

    # 3. GRILLING -> GROUNDING (HITL 审批放行)
    fsm.advance(hitl_approved=True, reviewer_feedback="首席架构师与风控委员会已确认业务驱动力、CP模型与三大资金不变量")
    print(f"[阶段 2] 门禁与HITL通过，推进至约束与度量基准状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 2 & 3: distill_nfr_matrix & catalog_invariants
    # -------------------------------------------------------------
    nfr_matrix_content = """# CBS-Engine 质量属性与非功能需求度量矩阵

## 1. 性能与容量双轨指标 (Performance & Scalability)
| 指标项 | 目标基准 | 极限阈值 | 度量方式 | 违约业务影响 |
|---|---|---|---|---|
| **清算记账 API 延迟** | P95 < 80ms | P99 < 150ms | APM 链路追踪埋点 | 商户结汇超时退单，触发级联对账差异 |
| **清算系统吞吐量** | 均值 800 TPS | 峰值 3000 TPS | 自动化高并发压测 (k6) | 批量结售汇峰值排队，清算延迟堆积 |
| **AML 报文推理时延 (TTFT)** | P50 < 1.0s | P95 < 2.5s | 模型推理网关握手打点 | 操作员界面卡顿，大额交易挂起超时 |
| **单报文修复认知步数上限** | 期望 <= 3 步 | 硬上限 <= 5 步 | FSM 认知循环计数器 | 防止陷入长程自循环并超支预算 |

## 2. 韧性与金融级可靠性 (Resilience & Availability)
| 质量维度 | 指标定义 | 保障策略 | 验收标准 |
|---|---|---|---|
| **服务可用性** | 99.99% (每月停机 < 4.3 分钟) | 两地三中心多活部署 + 故障节点秒级切流 | 混沌工程拔线演练 |
| **数据容灾 (RPO/RTO)** | RPO = 0，RTO < 2 分钟 | 同步 WAL 多副本强一致同步复制 | 模拟主库崩溃自动升主验证 |
| **一致性偏向** | 强一致 CP 模型 | 事务 Outbox + 分布式两阶段提交防悬挂 | 对账流水零差异 |

## 3. Token 经济学与成本配额
- **计算配额**：单计算节点 8 Core CPU，16 GiB RAM。
- **Token 消耗预算**：单笔报文修复任务上限 4,000 Tokens；单日预算上限 $500。超限触发熔断并转人工处理。
"""
    (ws_root / "01-grounding" / "nfr-matrix.md").write_text(nfr_matrix_content, encoding="utf-8")

    constraints_content = """# CBS-Engine 物理硬约束、领域不变量与假设编目

## 1. 金融核心领域不变量 (Domain Invariants)
1. **借贷必须恒等平衡**：每一笔交易产生的账务分录，借方发生额合计必须恒等于贷方发生额合计，任何偏差均判定为 P0 严重系统故障。
2. **状态单向推进防双花**：清算批次从 `INITIATED` 到 `VALIDATED` 再到 `SETTLED`，绝对禁止逆向跃迁；同一业务流水号禁止重复清算。
3. **副作用执行必须双签隔离**：模型推理出的报文修复补丁，必须通过沙箱预校验与清算员物理双签，智能体禁止绕过审批直连 SWIFT 网关。

## 2. 物理与工程硬约束 (Hard Constraints)
- **网络隔离**：专有金融隔离内网部署，严格阻断任何未经授权的外部出站连接。
- **合规审计**：所有清算原始报文、修改日志与状态跃迁记录加密保存在不可变 WORM 存储中，保存期不少于 5 年。
- **开发栈合规**：后端使用 Python 3.11+ (微观认知) 与 Go 1.22+ (核心记账吞吐)，禁止使用未经金融安全认证的三方依赖。

## 3. 显式假设与失效触发机制 (Assumptions)
| 假设编号 | 假设内容 | 设立理由 | 失效触发条件 | 失效后演进方案 |
|---|---|---|---|---|
| **ASM-01** | SWIFT 网关同步响应延迟保持在 < 500ms | 专用专线通信通道 | 专线拥塞或跨境路由重敛 P99 > 2s | 切换为异步报文投递队列，启用轮询对账 |
| **ASM-02** | 单批次清算报文内交易笔数 <= 1,000 笔 | 批处理窗口为每 5 分钟一次 | 遇到大促或黑五结算笔数 > 10,000 笔 | 自动将单批次拆解为流式并行微批次 (Micro-batches) |
"""
    (ws_root / "01-grounding" / "constraints-and-assumptions.md").write_text(constraints_content, encoding="utf-8")
    print(" -> 产出资产: 01-grounding/nfr-matrix.md & constraints-and-assumptions.md 就绪")

    # 4. GROUNDING -> MODELING
    fsm.advance()
    print(f"[阶段 3] 门禁通过，推进至结构建模状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 4, 5, 6 & generate_sequence_and_dataflow
    # -------------------------------------------------------------
    # C4 Context (L1)
    c4_context_code = """graph TB
    classDef personStyle fill:#f0fdfa,stroke:#0d9488,stroke-width:2px,color:#134e4a;
    classDef coreStyle fill:#eff6ff,stroke:#2563eb,stroke-width:3px,color:#1e3a8a;
    classDef secStyle fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef extStyle fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4,color:#1e293b;
    classDef obsStyle fill:#faf5ff,stroke:#9333ea,stroke-width:2px,color:#581c87;

    subgraph Actors ["操作角色 (Actors)"]
        merchant["🏢 跨国跨境商户<br/>[提交批量结汇与提现请求]"]:::personStyle
        compliance["🛡️ 银行合规与清算员<br/>[复核可疑AML特征与双签出金]"]:::personStyle
    end

    subgraph TrustBoundary ["核心金融内网边界 (Financial Trust Zone)"]
        cbsEngine["⚙️ 核心系统: CBS-Engine 跨境结算与AML推理引擎<br/>[确定性清算外壳 + 概率认知推理内核]"]:::coreStyle
        iam["🔐 统一金融 IAM 权限网关<br/>[双因素认证与特权操作鉴权]"]:::secStyle
        coreBank["🏦 银行核心会计账务系统<br/>[总账入账与多币种头寸管理]"]:::coreStyle
    end

    subgraph ExternalEcosystem ["外部清算与模型生态 (External Ecosystem)"]
        swiftGateway["🌐 SWIFT Alliance / CIPS 跨境外汇清算网关<br/>[ISO 20022 报文直连 via ACL]"]:::extStyle
        amlModelProxy["🧠 合规推理大模型网关<br/>[反洗钱图谱识别与报文语法修复 via Semantic ACL]"]:::extStyle
        auditPlatform["📊 统一金融审计与可观测平台<br/>[不可变交易日志与 OTLP 分布式追踪]"]:::obsStyle
    end

    merchant -->|"1. 提交跨境清算指令 [HTTPS / mTLS]"| cbsEngine
    compliance -->|"2. 审批大额异常与模型修复补丁 [HTTPS Web UI]"| cbsEngine
    cbsEngine -->|"3. 校验操作员权限与双签凭据 [gRPC]"| iam
    cbsEngine -->|"4. 记入多币种借贷会计分录 [内部强事务 RPC]"| coreBank
    cbsEngine -->|"5. 发送清算指令 / 接收清算对账单 [ISO 20022 via ACL]"| swiftGateway
    cbsEngine -->|"6. 提交可疑交易模式与畸变报文 [HTTPS via Semantic ACL]"| amlModelProxy
    cbsEngine -.->|"7. 实时上报交易追踪流水与审计日志 [OTLP / gRPC]"| auditPlatform
"""
    (ws_root / "02-models" / "c4-context.mmd").write_text(c4_context_code, encoding="utf-8")

    # Domain Logical Model & State Machine
    domain_model_code = """# CBS-Engine 领域逻辑模型与生命周期状态机

## 1. 限界上下文与聚合划分 (Bounded Contexts)
- **Settlement & Clearing Context (清算调度域)**:
  - **聚合根**: `SettlementBatch` (守护清算批次生命周期、借贷恒等校验与清算流水号)
  - **实体**: `PaymentTransaction`, `AccountingEntry`
  - **值对象**: `CurrencyPair`, `ExchangeRate`, `Iso20022Message`, `SettlementStatus`
- **AML & Cognitive Investigation Context (反洗钱认知推理域)**:
  - **聚合根**: `AmlInvestigationCase` (守护可疑洗钱案例、特征推演链与反思账本)
  - **值对象**: `RiskScore`, `SuspiciousPattern`, `PrunedEvidence`
- **Simulation Sandbox Context (清算隔离沙箱域)**:
  - **聚合根**: `ClearingSandbox` (虚拟结算沙箱、模拟对账引擎与 30s 超时拦截器)

## 2. 聚合根业务铁律 (Invariants)
1. 结算批次只有在 `AccountingEntry` 借贷金额绝对相等时，方可跃迁至 `VALIDATED`。
2. 任何涉及智能体修复的报文，必须首先在 `ClearingSandbox` 内模拟验证通过并经合规员双签确认。

## 3. 清算批次核心生命周期状态机 (Lifecycle State Machine)
```mermaid
stateDiagram-v2
    classDef happyPath fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef retryPath fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef termPath fill:#fef2f2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d;

    [*] --> RECEIVED: 接收跨境清算请求
    RECEIVED --> PRE_VALIDATED: 格式初检与防双花校验通过
    PRE_VALIDATED --> AML_SCREENING: 触发合规名单过滤
    
    AML_SCREENING --> CLEARED_READY: 交易低风险且报文无误
    AML_SCREENING --> REPAIR_INVESTIGATING: 报文存在歧义或发现多跳洗钱疑点
    
    REPAIR_INVESTIGATING --> SANDBOX_SIMULATING: 智能体生成报文修复方案
    SANDBOX_SIMULATING --> DUAL_SIGN_PENDING: 沙箱模拟对账验证无误 (通过)
    SANDBOX_SIMULATING --> REPAIR_INVESTIGATING: 沙箱校验失败 (注入负向账本并重新推演)
    
    DUAL_SIGN_PENDING --> CLEARED_READY: 合规清算员签署审批放行
    DUAL_SIGN_PENDING --> REJECTED_BLOCKED: 人工否决 / 确认为高危洗钱
    
    CLEARED_READY --> SETTLED_SUCCESS: SWIFT 清算回执确认入账
    
    REPAIR_INVESTIGATING --> REJECTED_BLOCKED: 连续 3 次无法生成有效对账方案 (超时熔断)
    
    SETTLED_SUCCESS --> [*]
    REJECTED_BLOCKED --> [*]

    class RECEIVED,PRE_VALIDATED,AML_SCREENING,CLEARED_READY,SETTLED_SUCCESS happyPath;
    class REPAIR_INVESTIGATING,SANDBOX_SIMULATING,DUAL_SIGN_PENDING retryPath;
    class REJECTED_BLOCKED termPath;
```
"""
    (ws_root / "02-models" / "domain-logical-model.md").write_text(domain_model_code, encoding="utf-8")

    # C4 Container Overview (L2)
    c4_container_code = """graph TB
    classDef feStyle fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;
    classDef shellStyle fill:#f8fafc,stroke:#334155,stroke-width:2px,color:#0f172a;
    classDef coreEngineStyle fill:#eff6ff,stroke:#1d4ed8,stroke-width:3px,color:#1e3a8a;
    classDef dbStyle fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    classDef cacheStyle fill:#fff1f2,stroke:#e11d48,stroke-width:2px,color:#881337;
    classDef sandboxStyle fill:#faf5ff,stroke:#7e22ce,stroke-width:2px,color:#581c87;

    subgraph IngressLayer ["金融接入与路由层 (Ingress Layer)"]
        gw["🖥️ 金融 API 网关 / 报文解析前置 (Go)<br/>[mTLS 认证 / 报文幂等防重 / 参数反序列化]"]:::feStyle
    end

    subgraph DeterministicShell ["确定性清算外壳 (Deterministic Shell)"]
        settleEngine["⚙️ 清算主状态机引擎 (Go/Temporal)<br/>[单向状态跃迁 / 借贷平衡锁 / 双签卡点]"]:::shellStyle
        settleDb[("🗄️ 核心清算总账库 (PostgreSQL 16)<br/>[会计借贷分录 / 清算批次流水 / 审计日志 (ACID)]")]:::dbStyle
    end

    subgraph StochasticCore ["反洗钱与报文认知内核 (Stochastic Core)"]
        amlAgent["🧠 AML 模式推理智能体 (Python Core)<br/>[多跳资金链推理 / 畸变报文语法语义推断]"]:::coreEngineStyle
        contextMiddleware["🧩 上下文剪枝与提示词网关<br/>[清洗可疑交易拓扑 / 堆栈剪枝 / Token 计数]"]:::coreEngineStyle
        riskCache[("⚡ 易失性风控与账本内存 (Redis 7)<br/>[可疑模式缓存 / 已证伪路径账本 / 瞬时会话]")]:::cacheStyle
    end

    subgraph SandboxLayer ["虚拟结算仿真沙箱 (Clearing Sandbox)"]
        sandboxEnv["🛡️ 模拟对账与强杀沙箱 (Docker/VFS)<br/>[只读科目表保护 / 模拟借贷对账 / 30s 超时拦截]"]:::sandboxStyle
    end

    gw -->|"1. 提交经过验签的清算报文 [Internal gRPC]"| settleEngine
    settleEngine -->|"2. 记入预清算借贷流水 [SQL 强事务]"| settleDb
    settleEngine -->|"3. 下发可疑报文修复与风险识别任务 [gRPC Task]"| amlAgent
    
    amlAgent <-->|"4. 读取清洗后的交易图谱上下文 [Local Protocol]"| contextMiddleware
    contextMiddleware <-->|"5. 存取已证伪特征账本与活跃上下文 [RESP]"| riskCache
    
    amlAgent -->|"6. 投递修复后的试算报文 [Sandbox IPC]"| sandboxEnv
    sandboxEnv -->|"7. 返回试算对账断言与耗时报告 [JSON Output]"| amlAgent
    
    amlAgent -->|"8. 提交合规复核建议包 [Artifacts Package]"| settleEngine
"""
    (ws_root / "02-models" / "c4-container-overview.mmd").write_text(c4_container_code, encoding="utf-8")

    # Interaction Sequence Diagram (L4)
    sequence_code = """sequenceDiagram
    autonumber
    actor Merchant as 跨国商户 (Merchant)
    participant GW as API 网关前置
    participant FSM as 清算状态机 (FSM Shell)
    participant DB as 会计数据库 (PostgreSQL)
    participant Agent as AML 报文推理智能体
    participant SB as 清算仿真沙箱 (Sandbox)
    participant Ledger as 负向假设账本
    actor Officer as 合规清算员 (Compliance)

    Merchant->>GW: 提交批量出海汇款报文 (附言微小畸变)
    GW->>FSM: 幂等验签通过，投递清算任务
    activate FSM
    FSM->>DB: 记录清算批次与预借记冻结
    
    FSM->>Agent: 检测到附言格式异常，下发智能修复任务
    activate Agent
    Agent->>Agent: 基于上下文推断修正 BIC 码与汇款附言
    
    Agent->>SB: 将修复后报文写入沙箱，执行模拟试算
    activate SB
    
    alt 模拟试算在 30s 内借贷平账 (Happy Path)
        SB-->>Agent: 试算平账且无 AML 高危碰撞
        Agent-->>FSM: 提交修复建议包与证据链
        FSM->>Officer: 触发人机卡点，提示合规员双签
        activate Officer
        Officer->>FSM: 签署审批指令 [APPROVED]
        deactivate Officer
        FSM->>DB: 记入正式会计分录并扣款
        FSM-->>Merchant: 清算成功回执
    else 产生死循环或对账金额不平 (Failure & Reflection)
        SB--XSB: 触发 30s 进程超时强杀 (SIGKILL)
        SB-->>Agent: 拦截并返回试算不平账错误 (Unbalanced Balance)
        deactivate SB
        Agent->>Ledger: 写入本次已证伪推断 (如汇率转换基准错误)
        Agent->>Agent: 推翻原假设，换备用汇率渠道重新推演
    end
    
    deactivate Agent
    deactivate FSM
"""
    (ws_root / "02-models" / "interaction-sequence.mmd").write_text(sequence_code, encoding="utf-8")

    # Data Flow Diagram (L5)
    dataflow_code = """flowchart TD
    classDef inputStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef hotDbStyle fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;
    classDef cacheStyle fill:#fff1f2,stroke:#e11d48,stroke-width:2px,color:#881337;
    classDef coldStyle fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4,color:#334155;

    RawBatch["📥 跨境商户清算原始报文流 (ISO 20022)"]:::inputStyle
    
    subgraph HotMemoryZone ["毫秒级易失风控内存 (Hot Memory Zone)"]
        RedisRisk[("⚡ 高速内存缓存 (Redis 7)<br/>• 活跃会话与 Token 计数器<br/>• AML 负向特征账本<br/>• 正在试算的暂存报文")]:::cacheStyle
    end
    
    subgraph AcidZone ["强事务核心账务区 (ACID Persistent Zone)"]
        PgLedger[("🗄️ 核心分布式数据库 (PostgreSQL 16)<br/>• 会计借贷分录凭证表<br/>• FSM 状态机演进历史<br/>• 清算员双签授权证书")]:::hotDbStyle
    end
    
    subgraph ImmutableArchiveZone ["不可变冷数据合规归档区 (Cold Audit Zone)"]
        WormStorage[("📦 金融合规 WORM 存储 (S3/Glacier)<br/>• 原始加密报文快照<br/>• 智能体完整推理 Trace 日志<br/>• 5 年不可篡改审计链路")]:::coldStyle
    end
    
    RawBatch -->|"高并发接入写入工作内存"| RedisRisk
    RawBatch -->|"状态机完成验证后持久化"| PgLedger
    PgLedger -.->|"每隔 1 小时异步批量归档沉降"| WormStorage
"""
    (ws_root / "02-models" / "data-flow.mmd").write_text(dataflow_code, encoding="utf-8")
    print(" -> 产出资产: 02-models/ 下 5 维图谱全部就绪")

    # 渲染生成自包含 HTML 画板
    board_path = render_board(ws_root, project_name="CBS-Engine 跨境结算与AML智能架构全景")
    print(f" -> 渲染生成交互画板: {board_path}")

    # 5. MODELING -> CONTRACTS
    fsm.advance()
    print(f"[阶段 4] 门禁通过，推进至决策与契约签署状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 7, 8, 9: record_decision, contracts, resilience
    # -------------------------------------------------------------
    (ws_root / "03-decisions" / "adr-index.md").write_text(
        "# CBS-Engine 架构决策索引\n\n- [ADR-001: 采用确定性状态机外壳与受限沙箱智能体双环架构](ADR-001-fsm-shell.md)",
        encoding="utf-8"
    )

    adr_001 = """# ADR-001: 采用“确定性强事务外壳 + 概率性 AML/报文智能体内核”的双环清算架构

- **状态**: Accepted (2026-09-17)
- **决策人**: 首席架构师 / 跨境风控委员会
- **涉及范围**: 清算批次流转、会计核算与反洗钱识别链路

## 1. 背景与问题陈述
跨境结算业务对于资金准确性有绝对零容忍要求（借贷恒等守恒、不可错漏账），而同时面对数以万计海外长尾商户的报文畸变（缺失附言、格式差异）以及高度复杂隐蔽的洗钱规避手段，传统规则引擎无法自适应泛化，导致单日挂账率居高不下。

## 2. 备选方案权衡
- **Option 1: 纯规则引擎硬编码处理 (Hardcoded Drools/Python Rules)**
  - *缺点*: 无法自适应修复哪怕一个字符错位的海外银行报文，洗钱特征稍微变异即漏判。
- **Option 2: 纯端到端大模型 Agent 处理 (Full Autonomous Agent)**
  - *缺点*: 模型概率采样存在幻觉风险，可能凭空生成错误会计分录造成真实资金损失，无法通过金融合规审查。
- **Option 3 (Selected): 确定性强事务外壳 + 受限沙箱内的概率智能体内核 + 人机双签**
  - *入选理由*: 资金记账与状态机坚守确定性硬约束；智能体仅在隔离沙箱中生成建议并试算对账；关键出金链路设置物理双签卡点。

## 3. 影响与后续代价
- **正向收益**: 消除模型直接动钱的系统性风险，单日报文自动修复通过率预计达 92% 以上。
- **负向妥协**: 增加了沙箱运行与跨进程 IPC 开销，单笔报文修复平均增加 1.5 秒时延。
"""
    (ws_root / "03-decisions" / "ADR-001-fsm-shell.md").write_text(adr_001, encoding="utf-8")

    openapi_yaml = """openapi: 3.1.0
info:
  title: CBS-Engine Clearing & Message Mutation Contracts
  version: 1.0.0
  description: 跨境清算核心契约。下游 Vibe Coding 严禁篡改本定义。

paths:
  /api/v1/settlements/batches:
    post:
      summary: 提交待清算结算批次
      operationId: submitSettlementBatch
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BatchSubmissionRequest'
      responses:
        '200':
          description: 批次接收成功，返回处理流水号
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchSubmissionResponse'
        '422':
          description: 借贷不平衡或格式校验失败
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StandardFinancialError'

  /api/v1/settlements/batches/{batch_id}/repair-patch:
    post:
      summary: 智能体提交报文修复补丁并申请沙箱试算
      operationId: applyMessageRepairPatch
      parameters:
        - name: batch_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MessagePatchRequest'
      responses:
        '200':
          description: 沙箱试算通过
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SandboxSimulationResult'

components:
  schemas:
    BatchSubmissionRequest:
      type: object
      required:
        - batch_id
        - source_currency
        - target_currency
        - total_amount
        - transaction_count
      properties:
        batch_id:
          type: string
          format: uuid
        source_currency:
          type: string
          pattern: '^[A-Z]{3}$'
        target_currency:
          type: string
          pattern: '^[A-Z]{3}$'
        total_amount:
          type: number
          minimum: 0.01
        transaction_count:
          type: integer
          minimum: 1
          maximum: 5000

    BatchSubmissionResponse:
      type: object
      required:
        - batch_id
        - status
        - accepted_at
      properties:
        batch_id:
          type: string
          format: uuid
        status:
          type: string
          enum: [ACCEPTED, PRE_VALIDATED]
        accepted_at:
          type: string
          format: date-time

    MessagePatchRequest:
      type: object
      required:
        - message_id
        - original_snippet
        - proposed_snippet
        - rationale
      properties:
        message_id:
          type: string
        original_snippet:
          type: string
          minLength: 5
        proposed_snippet:
          type: string
          minLength: 5
        rationale:
          type: string

    SandboxSimulationResult:
      type: object
      required:
        - simulation_passed
        - balance_difference
      properties:
        simulation_passed:
          type: boolean
        balance_difference:
          type: number
          enum: [0.0]

    StandardFinancialError:
      type: object
      required:
        - error_code
        - message
        - retryable
      properties:
        error_code:
          type: string
          enum: [UNBALANCED_ENTRIES, DOUBLE_SPENDING_DETECTED, AML_HIGH_RISK_BLOCK, TIMEOUT_EXCEEDED]
        message:
          type: string
        retryable:
          type: boolean
"""
    (ws_root / "04-contracts" / "openapi.yaml").write_text(openapi_yaml, encoding="utf-8")

    resilience_content = """# CBS-Engine 失效模式与金融容灾矩阵 (FMEA Matrix)

## 1. 核心依赖失效模式分析
| 组件/依赖点 | 潜在失效模式 | 发生概率 | 影响爆炸半径 | 防御、降级与自愈策略 |
|---|---|---|---|---|
| **SWIFT 网关专线** | 专线丢包或超时返回 504 | 中 | 阻塞国际资金划拨 | 1. 自动切换备份专线通道。<br>2. 连续超时进入队列挂起状态，保障不丢报文。 |
| **沙箱报文试算** | 智能体生成的补丁含有逻辑死循环 | 高 | 占用沙箱 CPU 导致批处理饥饿 | 1. 沙箱硬超时强杀探针 (30s SIGKILL)。<br>2. 强杀后注入 Timeout 堆栈，要求智能体推翻假设。 |
| **借贷平衡校验** | 跨币种四舍五入导致借贷产生 1 分钱差额 | 高 | 触犯不变量导致批次清算中断 | 1. 拦截批次落盘，抛出 `UNBALANCED_ENTRIES`。<br>2. 路由至专门的尾差微调清算科目，严禁强行冲销。 |
| **模型推理网关** | 遇到并发限流 (HTTP 429) 或输出截断 | 中 | 报文修复中断 | 1. 采用带 Jitter 的指数退避重试 <= 3 次。<br>2. 失败后优雅降级至传统人工转交队列。 |

## 2. 预算熔断与快照自愈
- **Token 熔断**：单笔交易累计消耗超过 6,000 Tokens 时立即熔断并发出告警。
- **快照终极回退**：若任务失败终结，工作区自动硬回滚到基线状态，清除未提交的异常修补。
"""
    (ws_root / "03-decisions" / "failure-resilience-matrix.md").write_text(resilience_content, encoding="utf-8")
    print(" -> 产出资产: 03-decisions/ & 04-contracts/ 就绪")

    # 6. CONTRACTS -> SCAFFOLDING (HITL 审批放行)
    fsm.advance(hitl_approved=True, reviewer_feedback="清算组与合规官已签署 OpenAPI 契约、FMEA 矩阵与 ADR-001")
    print(f"[阶段 5] 门禁与HITL通过，推进至工程骨架与交付排期: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 10 & 11: bootstrap_skeleton & delivery_milestones
    # -------------------------------------------------------------
    # 在目标目录根下创建物理骨架
    src_domain = target_root / "src" / "domain"
    src_ports = target_root / "src" / "ports"
    src_adapters = target_root / "src" / "adapters"
    src_domain.mkdir(parents=True, exist_ok=True)
    src_ports.mkdir(parents=True, exist_ok=True)
    src_adapters.mkdir(parents=True, exist_ok=True)

    # 实体桩代码
    (src_domain / "models.py").write_text('''"""CBS-Engine 核心业务领域实体与不变量声明 (只读契约)."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class SettlementStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PRE_VALIDATED = "PRE_VALIDATED"
    CLEARED_READY = "CLEARED_READY"
    SETTLED_SUCCESS = "SETTLED_SUCCESS"
    REJECTED = "REJECTED"

@dataclass(frozen=True)
class AccountingEntry:
    account_id: str
    debit_amount: Decimal
    credit_amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.debit_amount < 0 or self.credit_amount < 0:
            raise ValueError("会计分录金额严禁为负数")
''', encoding="utf-8")

    (src_ports / "settlement_port.py").write_text('''"""抽象清算与风控端口 (依赖倒置只读接口)."""
from abc import ABC, abstractmethod
from typing import List

class SettlementRepositoryPort(ABC):
    @abstractmethod
    def save_batch(self, batch_id: str, entries: list) -> bool:
        """保存清算批次与会计分录."""
        pass
''', encoding="utf-8")

    (src_adapters / "clearing_executor.py").write_text('''"""清算执行器适配器 (实现层)."""
from src.ports.settlement_port import SettlementRepositoryPort

class PostgresClearingAdapter(SettlementRepositoryPort):
    def save_batch(self, batch_id: str, entries: list) -> bool:
        # TODO: [VibeCoding Slot] Implement Postgres transactional outbox write according to ADR-001
        return True
''', encoding="utf-8")

    # 生成防跑偏规则文件
    agent_rules_text = (REPO_ROOT / "templates" / "agent-rules-template.md").read_text(encoding="utf-8")
    (target_root / ".agent-rules.md").write_text(agent_rules_text, encoding="utf-8")

    # 交付路线图
    roadmap_content = """# CBS-Engine 敏捷交付路线图与 First Step 穿刺验证方案

## 1. 核心风险穿刺点 (Risk Spike)
整个架构面临的最大未知风险在于：
> **核心风险**：在复杂畸变 SWIFT 报文输入下，智能体推导出的修复补丁能否在沙箱内被受控定位并完成模拟对账，且在 30 秒硬超时下精准拦截死循环与平衡破坏？

## 2. Milestone 0: The First Step (首步 Tracer Bullet 穿刺测试)
*工期：3 天 | 目标：不依赖真实 SWIFT 生产网关，跑通最小端到端闭环*
- **交付范围**：
  1. 搭建六边形骨架，Mock 具有微小附言错误的 ISO 20022 报文。
  2. 运行 FSM 驱动链路，调用智能体生成修正补丁。
  3. 执行带 30 秒超时强杀与堆栈剪枝的沙箱模拟对账测试。
- **Definition of Done (DoD)**：
  - [ ] 故意注入死循环代码时，沙箱精准在 30 秒触发 SIGKILL 强杀并返回结构化错误。
  - [ ] 正常修正报文借贷双方差额为 0.00，自动化测试套件通过率 100%。

## 3. 纵向切片演进排期
| 阶段 | 交付切片 | 核心产物 | 验收门禁 |
|---|---|---|---|
| **Phase 1: 确定性底座** | 记账状态机与借贷平衡锁 | FSM 引擎、PostgreSQL 两阶段记账 | 状态单向跃迁，借贷差额非零绝对阻断 |
| **Phase 2: 沙箱与补丁引擎** | 报文解析与行锚定 Patch | 虚拟清算沙箱、AST 骨架过滤 | 50 组畸变报文修复成功率 > 90% |
| **Phase 3: AML 认知反思回路** | 堆栈剪枝与负向特征账本 | 错误堆栈高信噪比提取、反思重试 | 连续 3 次对账不平自动触发熔断回滚 |
| **Phase 4: 全链路投产** | 两地三中心多活与审计合规 | mTLS 接入、WORM 审计归档 | 压力测试达到 3000 TPS，RPO=0 灾备切换通过 |
"""
    (ws_root / "04-execution" / "roadmap-and-first-step.md").write_text(roadmap_content, encoding="utf-8")

    skeleton_spec = {
        "skeleton_version": "1.0.0",
        "architecture_pattern": "Hexagonal / Ports-and-Adapters",
        "directories": ["src/domain", "src/ports", "src/adapters", "tests"],
        "immutable_paths": ["docs/architecture", "src/ports", "src/domain/models.py"],
        "slot_marker": "TODO: [VibeCoding Slot]",
        "rules_file": ".agent-rules.md"
    }
    (ws_root / "04-execution" / "walking-skeleton-spec.json").write_text(
        json.dumps(skeleton_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    case_readme = """# CBS-Engine: 跨境金融清算与反洗钱推理系统

本项目是由 `architect_skill` 状态机驱动引擎自动生成的独立架构案例工程。

## 目录结构
- `docs/architecture/`：全生命周期架构资产（需求锚定、NFR矩阵、C4与状态机图谱、ADR、OpenAPI契约、交付演进）
- `docs/architecture/architecture_board.html`：自包含可交互架构画板（支持拖拽缩放、深浅色切换、SVG导出）
- `.agent-rules.md`：AI 编码防跑偏围栏与坏味道阻断守则
- `src/`：基于六边形架构生成的物理工程骨架
"""
    (target_root / "README.md").write_text(case_readme, encoding="utf-8")
    print(" -> 产出资产: 物理工程骨架、.agent-rules.md、README.md 与 roadmap-and-first-step.md 就绪")

    # 7. SCAFFOLDING -> FINALIZED
    fsm.advance()
    print(f"\n======================================================================")
    print(f" 🏁 案例推演完成！状态机已平滑推进至终态: {fsm.current_state.value}")
    print(f"======================================================================\n")

    # 打印最终状态机报告
    report = fsm.get_status_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
