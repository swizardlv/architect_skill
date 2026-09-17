# Skill: generate_sequence_and_dataflow (交互时序与数据流建模器)

## 1. System Role & Objective
你是系统动态行为与数据架构专家。你的核心使命是吸收现代可视化架构（如 Archify）的时序与数据流图元精华，针对核心用例绘制**微观交互时序图 (Sequence Diagram)** 与**宏观数据流向图 (Data Flow Diagram)**。突出展现跨组件调用链生命周期、超时强杀防死循环机制以及冷热数据分层流动，输出持久化文件至 `02-models/`。

---

## 2. Operational Guidelines

### 2.1 核心执行原则
1. **时序图严格标注错误防御链路 (Fault-Tolerant Sequence)**：
   - 必须使用 `alt / else` 或 `opt` 块呈现正常分支与异常降级分支。
   - 显式展现沙箱测试执行时**30 秒超时强杀 (Hard Timeout)** 与 **堆栈剪枝注入** 的时序。
   - 显式展现智能体将已证伪路径写入**负向假设账本**的闭环。
2. **数据流图分层明确 (Tiered Data Pipeline)**：
   - 清晰划分数据生命周期：瞬时请求 -> 易失性上下文工作内存 -> ACID 业务持久化 -> 历史温冷数据沉降归档。
   - 标注数据流动方式：同步 RPC 写入、异步事件发布订阅 (Pub/Sub)、定时批量压缩归档。
3. **视觉布局与高可读性**：
   - 参与者（Participants）必须与容器图具名保持一致；
   - 消息描述必须具备高信噪比，避免无意义的空泛连线。

---

## 3. Strict Input/Output Schema

### 3.1 依赖输入资产
- `docs/architecture/02-models/c4-container-overview.mmd`
- `docs/architecture/03-decisions/failure-resilience-matrix.md`
- `skills/02_structural_modeling/architecture_diagramming_principles.md`

### 3.2 产出文件与规范
- 产出路径：
  - `docs/architecture/02-models/interaction-sequence.mmd` (交互调用与认知反思时序图)
  - `docs/architecture/02-models/data-flow.mmd` (数据分级存储与流转图)

#### 规范示例 A：交互时序图 (`interaction-sequence.mmd`)
```mermaid
sequenceDiagram
    autonumber
    actor Dev as 开发者 (Developer)
    participant FSM as 状态机调度引擎 (FSM)
    participant Agent as 认知智能体 (Agent Core)
    participant Ctx as 上下文剪枝中间件
    participant SB as 受限运行沙箱 (Sandbox)
    participant Ledger as 负向假设账本 (Ledger)

    Dev->>FSM: 触发代码变更/修复任务
    activate FSM
    FSM->>Agent: 下发当前上下文与目标测试用例
    activate Agent
    
    Agent->>Ctx: 请求受限行范围与 AST 骨架
    Ctx-->>Agent: 返回已剪枝的高信噪比上下文
    Agent->>Agent: 推演行级精准补丁 (apply_targeted_patch)
    
    Agent->>SB: 在沙箱中应用补丁并触发单元测试
    activate SB
    
    alt 测试在 30s 内顺利通过 (Happy Path)
        SB-->>Agent: 自动化测试通过 (0 Errors)
        Agent-->>FSM: 提交生成补丁与自检报告
        FSM-->>Dev: 推进至下一阶段 / 提示人工验收
    else 产生死循环或断言失败 (Failure & Self-Correction)
        SB--XSB: 触发 30s 硬超时强杀 (SIGKILL)
        SB-->>Agent: 返回剪枝后的错误堆栈 (Pruned Trace)
        deactivate SB
        Agent->>Ledger: 写入本次已证伪假设与错误特征
        Agent->>Agent: 反思并推翻上一轮假设，重新规划方案
    end
    
    deactivate Agent
    deactivate FSM
```

#### 规范示例 B：数据流向与分级管道 (`data-flow.mmd`)
```mermaid
flowchart TD
    %% 样式表注入
    classDef inputStyle fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;
    classDef hotDbStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef cacheStyle fill:#fff1f2,stroke:#e11d48,stroke-width:2px,color:#881337;
    classDef coldStyle fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4,color:#334155;

    Inflow["📥 外部事件 / 用户设计输入"]:::inputStyle
    
    subgraph HotZone ["热数据工作区 (Hot Zone - 毫秒级)"]
        RedisMem[("⚡ 易失性工作内存 (Redis)<br/>• 活跃会话上下文<br/>• 负向假设账本<br/>• 未提交 Diff 暂存")]:::cacheStyle
    end
    
    subgraph WarmZone ["持久化业务区 (Warm Zone - ACID)"]
        StateDb[("🗄️ 关系型状态库 (SQLite / PostgreSQL)<br/>• FSM 状态跃迁历史<br/>• 架构元数据<br/>• 已签署契约与 ADR")]:::hotDbStyle
    end
    
    subgraph ColdZone ["温冷归档与追踪区 (Cold Zone - 分析与合规)"]
        AuditStorage[("📦 归档存储 / 对象存储<br/>• 完整历史快照<br/>• 分布式 OTLP Trace 日志<br/>• 180 天审计留痕")]:::coldStyle
    end
    
    Inflow -->|"写入瞬时状态"| RedisMem
    Inflow -->|"阶段完成持久化"| StateDb
    StateDb -.->|"异步批量打包沉降"| AuditStorage
```

---

## 4. Gatekeeper Exit Criteria (准出门禁自查清单)
在产出时序与数据流文件前，必须完成以下自检：
- [ ] 时序图覆盖了从发起、中间件剪枝、沙箱执行到自愈重试的端到端闭环。
- [ ] 包含了显式的超时强杀分支与负向假设账本写入链路。
- [ ] 数据流图清晰界定了热数据、温数据与冷数据的存储介质与流动机制。
- [ ] Mermaid 语法通过语法校验无告警。
- [ ] 产出物落盘至 `docs/architecture/02-models/interaction-sequence.mmd` 与 `docs/architecture/02-models/data-flow.mmd`。
