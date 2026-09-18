# 概念数据模型规约 (Conceptual Data Model, CDM)

> **架构视角**: 数据视角顶层抽象 (Data Architecture - Conceptual Level)  
> **核心使命**: 遵循“CDM $\to$ LDM $\to$ PDM”演进路径，用业务统一语言厘清架构技能编排与治理套件的核心业务实体、实体关系基数（Cardinality）与组件所有权边界。保持技术中立，严禁引入任何物理数据库实现细节。

---

## 1. 统一语言与领域概念字典 (Ubiquitous Language Dictionary)

| 概念术语 (Term) | 英文标识 (Identifier) | 商业定义与业务语义 | 概念边界与排他性澄清 |
| :--- | :--- | :--- | :--- |
| **架构设计任务** | `ArchitectureJob` | 架构师发起的包含目标愿景、范围边界与质量准则的顶层设计工作单元。 | 区别于单一会话或临时脚本，任务承载完整的工程生命周期。 |
| **阶段里程碑** | `PhaseMilestone` | 架构推导流转中确立的不可逆业务阶段（如需求提炼、结构建模、验证放行）。 | 业务进度管控点，不绑定具体的调度线程或定时器。 |
| **门禁断言** | `GatekeeperAssertion` | 阶段推进前必须满足的不可妥协质量与完整性规则校验判定。 | 形式化质量守卫契约，独立于具体代码单测实现。 |
| **架构工件** | `ArchitectureArtifact` | 阶段推导输出的受版本管理的工程技术交付物（如 AOD、CM、OM、CDM、ADR）。 | 系统向干系人交付的价值凭证，不指代物理磁盘文件句柄。 |
| **审查批注** | `ReviewFeedback` | 技术委员会评审人或自动化门禁引擎在工件审查时留下的整改意见或签署记录。 | 包含明确的处置决议与审计痕迹，具有治理约束力。 |
| **统一词汇条目** | `GlossaryEntry` | 业务与技术团队共同认可并严格遵守的领域核心概念与统一语言定义。 | 跨工件一致性基准，消除跨团队沟通歧义。 |
| **认知会话** | `CognitiveSession` | Agent 承载特定架构治理任务的完整多轮认知交互生命周期，包含 Token 预算与安全策略。 | 贯穿生命周期的认知容器，不同于单次无状态 HTTP 请求。 |
| **执行步骤** | `ExecutionStep` | Agent 在单轮推导中产生的思考快照（Thought）、工具调用（Action）与环境反馈（Observation）。 | 一等公民实体，支持时间旅行重放调试（Time-travel Debugging）。 |
| **负向假设** | `NegativeHypothesis` | 经沙箱验证失败或门禁拦截的错误探索路径与反思规则。 | 系统的“失败账本”，避免重试循环重复踩坑。 |

---

## 2. 概念实体关系拓扑图 (Conceptual ER Diagram)

```mermaid
erDiagram
    %% 核心概念实体关系图谱 (严格业务语义与基数标注)
    ARCHITECTURE_JOB ||--|{ PHASE_MILESTONE : "推进经历 (Progresses Through)"
    PHASE_MILESTONE ||--|{ GATEKEEPER_ASSERTION : "准入评估 (Evaluates)"
    PHASE_MILESTONE ||--o{ ARCHITECTURE_ARTIFACT : "产出交付 (Produces)"
    ARCHITECTURE_ARTIFACT ||--o{ REVIEW_FEEDBACK : "接受审查 (Receives)"
    ARCHITECTURE_JOB ||--o{ GLOSSARY_ENTRY : "统一定义 (Defines)"
    GLOSSARY_ENTRY ||--o{ ARCHITECTURE_ARTIFACT : "规范约束 (Governs)"

    %% Agent AI 认知轨迹与一等状态实体
    ARCHITECTURE_JOB ||--o{ COGNITIVE_SESSION : "开辟执行 (Hosts)"
    COGNITIVE_SESSION ||--|{ EXECUTION_STEP : "记录步骤 (Logs Steps)"
    EXECUTION_STEP ||--o{ NEGATIVE_HYPOTHESIS : "沉淀证伪 (Generates)"

    ARCHITECTURE_JOB {
        string job_reference_id "架构任务唯一业务标识"
        string target_system_name "目标系统愿景全称"
        string architectural_style "主导架构模式风格"
        string governance_status "整体治理流转状态"
    }

    PHASE_MILESTONE {
        string milestone_phase_code "阶段里程碑编码"
        string phase_objective "阶段核心业务推导目标"
        boolean is_exit_approved "准出放行签署标志"
        datetime phase_transition_time "状态流转达成时间点"
    }

    GATEKEEPER_ASSERTION {
        string rule_code "门禁规则编码"
        string quality_dimension "质量属性维度"
        boolean evaluation_passed "断言通过判定"
        number compliance_score "合规度量得分"
    }

    ARCHITECTURE_ARTIFACT {
        string artifact_identifier "工件业务唯一编号"
        string artifact_category "工件类别"
        string semantic_version "工件逻辑版本号"
        string review_verdict "评审终局决议"
    }

    REVIEW_FEEDBACK {
        string feedback_reference "审查批注流水号"
        string reviewer_identity "评审人角色标识"
        string issue_severity "缺陷严重级别"
        string remediation_advice "整改优化建议"
    }

    GLOSSARY_ENTRY {
        string ubiquitous_term "统一领域术语"
        string business_definition "业务权威定义"
        string domain_context "适用限界子域"
    }

    COGNITIVE_SESSION {
        string session_reference_id "会话业务全局标识"
        string autonomy_level "自主度等级 (LoA-1至LoA-4)"
        number cumulative_token_cost "累计代币折算成本"
        string execution_state "会话运行状态"
    }

    EXECUTION_STEP {
        string step_sequence_id "步骤单调自增序号"
        string thought_snapshot "模型单步思考快照"
        string action_name "调用工具标识"
        string observation_summary "沙箱反馈观察快照"
        boolean has_side_effect "是否具有物理写副作用"
    }

    NEGATIVE_HYPOTHESIS {
        string failed_path_hash "证伪路径特征签名"
        string failure_root_cause "失败根因分类"
        string anti_repetition_rule "防重复踩坑避障规则"
    }
```

---

## 3. 核心实体详细规格卡片 (Core Entity Specifications)

### 3.1 实体: 架构设计任务 (ArchitectureJob)
- **归属概念子域**: 架构编排与生命周期治理域 (Orchestration & Governance)
- **核心商业特征**: 架构师发起系统设计的总顶层实体，协调各阶段里程碑演进并追踪总体质量合规状态。
- **关键业务属性**:
  - `job_reference_id`: 架构任务的全局业务唯一编号。
  - `target_system_name`: 待构建或治理的目标系统法定商业名称。
  - `governance_status`: 治理流转生命周期（定义中、结构建模中、评审门禁中、已归档发布）。
- **核心业务不变量 (Business Invariants)**:
  - 任务推进必须遵循单向阶段流转，任何跳阶段行为均被阻断。
  - 只有在所有必需阶段里程碑均获得准出放行后，任务才能转为“已归档发布”。

### 3.2 实体: 执行步骤 (ExecutionStep)
- **归属概念子域**: 轨迹可观测性与时间旅行重放域 (Trajectory Observability & Replay)
- **核心商业特征**: Agent 探索与工具调用过程中的一等公民实体，记录思考快照、执行行动与沙箱反馈。
- **关键业务属性**:
  - `step_sequence_id`: 步骤序号。
  - `thought_snapshot`: 模型思考快照（Thought）。
  - `action_name`: 调用的具体工具名（Action）。
  - `observation_summary`: 环境观察结果摘要（Observation）。
  - `has_side_effect`: 标记是否修改了本地文件或触发了外部提交。
- **核心业务不变量**:
  - 步骤实体一经写入不可更改，严格按照时间序列只增追加。
  - 若包含不可逆副作用，必须在对应工件中记录门禁审批通过标记。

### 3.3 实体: 负向假设 (NegativeHypothesis)
- **归属概念子域**: 失败反思与认知防线域 (Reflective Guardrails)
- **核心商业特征**: 记录经事实证伪的代码实现或架构推导分支，充当“失败账本”。
- **关键业务属性**:
  - `failed_path_hash`: 失败路径特征。
  - `failure_root_cause`: 语法错误、单测失败、门禁打回或死循环阻断。
  - `anti_repetition_rule`: 指导后续思考避免重复探索的规则。
- **核心业务不变量**:
  - 当尝试相同路径连续报错 3 次时，强制触发死循环熔断并生成不可撤销的负向假设记录。

---

## 4. 限界上下文与数据所有权矩阵 (Data Ownership Matrix)

| 概念实体 (Entity) | 所属限界上下文 (Bounded Context) | 唯一归属组件 (Owning CM Component) | 数据所有权模式 (Data Ownership) | 跨边界访问与流转契约 |
| :--- | :--- | :--- | :--- | :--- |
| **`ArchitectureJob`** | 编排治理上下文 | `LifecycleOrchestrator` (COMP-01) | **独占写入 (Exclusive Write)** | 驱动阶段状态机推进与通知 |
| **`PhaseMilestone`** | 编排治理上下文 | `LifecycleOrchestrator` (COMP-01) | **独占写入 (Exclusive Write)** | 汇总门禁断言决定流转 |
| **`GatekeeperAssertion`**| 质量门禁上下文 | `GatekeeperGuard` (COMP-02) | **独占写入 (Exclusive Write)** | 导出判定结果供里程碑放行参考 |
| **`ArchitectureArtifact`** | 工件交付上下文 | `ArtifactBuilder` (COMP-03) | **独占写入 (Exclusive Write)** | 向评审引擎与渲染看板暴露视图 |
| **`ReviewFeedback`** | 评审协作上下文 | `ReviewBoardHub` (COMP-04) | **独占写入 (Exclusive Write)** | 反馈修改意见并回传工件构建器 |
| **`GlossaryEntry`** | 领域知识上下文 | `KnowledgeDictionary` (COMP-05) | **独占写入 (Exclusive Write)** | 为所有工件生成提供统一词汇对照表 |
| **`CognitiveSession`** | 认知会话上下文 | `SessionGovernor` (COMP-06) | **独占写入 (Exclusive Write)** | 跟踪 Token 消耗与自主度授权 |
| **`ExecutionStep`** | 轨迹审计上下文 | `TrajectoryAuditor` (COMP-07) | **追加写入 (Append-Only Write)** | 提供单步回溯与时间旅行重放调试 |
| **`NegativeHypothesis`**| 反思避障上下文 | `ReflectionMemory` (COMP-08) | **独占写入 (Exclusive Write)** | 在规划循环前提供失败分支阻断依据 |

---

## 5. 四步压力测试与“重放审计”自检记录 (Stress Tests & Replay Walkthrough)

### 5.1 业务代言人对齐走查测试 (Business Proxy Walkthrough)
- **演练场景**: 首席架构师启动新交易系统设计任务，推导 AOD 与 CDM，在门禁校验中由于实体包含技术字段被拦截，经整改后顺利签署通过。
- **走查路径**:
  1. 架构师初始化 `ArchitectureJob`，关联系统愿景；
  2. 启动建模阶段 `PhaseMilestone`，从 `GlossaryEntry` 提取统一领域术语；
  3. 产出首版 `ArchitectureArtifact` (CDM)；
  4. 触发门禁，`GatekeeperAssertion` 检出违规项并记录未通过；
  5. 评审引擎生成 `ReviewFeedback` 指导整改；
  6. 修订后重新评估，合规评分通过，里程碑 `is_exit_approved` 置为真，驱动进入后续阶段。
- **评审结论**: 业务流转过程与架构师日常治理逻辑完全吻合，概念实体关系严密可信。

### 5.2 生命周期完整性测试 (Lifecycle & State Completeness)
- **被测核心实体**: `ArchitectureJob` 与 `ArchitectureArtifact`。
- **状态全集检查**:
  - `ArchitectureJob`: [Initiated] $\to$ [AnalysisActive] $\to$ [ModelingActive] $\to$ [UnderReview] $\to$ [ApprovedAndFinalized] / [RejectedTerminated]。
  - `ArchitectureArtifact`: [Draft] $\to$ [InReview] $\to$ [Accepted] / [RequiresRevision]。
- **评审结论**: 实体包含所有必要的状态属性与追溯标记，无孤立断流。

### 5.3 驱动组件模型 (CM) 验证测试
- **所有权单一性检查**:
  - 确认仅 `GatekeeperGuard` 可生成和更新 `GatekeeperAssertion` 状态，工件构建器仅有读权限。
  - 确认 `ReviewFeedback` 仅由 `ReviewBoardHub` 维护，杜绝跨边界篡改评审记录。
- **评审结论**: CDM 实体与逻辑组件边界严格映射，各司其职，保证系统的松耦合与内聚性。

### 5.4 “重放与审计”实战验证测试 (The Replay Walkthrough)
- **核验手段**: 选取一笔在文档打磨中被拦截违规写操作的 Agent 执行轨迹，依据 CDM 实体关系进行单步追溯。
- **重放推演**: 依据 `ExecutionStep` 记录，成功还原出模型在第 3 步生成的推导思路（Thought）、调用的文件编辑指令与具体参数（Action），以及打磨器拦截扣分报错反馈（Observation），并验证了生成的 `NegativeHypothesis` 成功阻断了模型重复尝试该写操作。
- **评审结论**: 概念实体支撑 100% 细节回溯与时间旅行重放调试（Time-travel Debugging），数据模型具备工业级可观测性与可审计性。
