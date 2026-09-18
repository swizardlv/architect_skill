# 架构全景概览图规约 (Architecture Overview Diagram, AOD)

> 架构视角：系统全局逻辑全景 (Global Overview & Cognitive Plane)  
> 核心作用：面向高层干系人与业务负责人的高阶抽象图，展示系统边界、认知控制平面、上下文状态域、执行沙箱、模型网关与横切安全围栏。

---

## 1. AOD 架构全景抽象图 (Mermaid Visual)

```mermaid
flowchart TB
    %% 样式体系定义
    classDef ingressStyle fill:#f0fdfa,stroke:#0d9488,stroke-width:2px,color:#134e4a;
    classDef routerStyle fill:#fefce8,stroke:#ca8a04,stroke-width:2px,color:#713f12;
    classDef coreStyle fill:#eff6ff,stroke:#2563eb,stroke-width:3px,color:#1e3a8a;
    classDef sandboxStyle fill:#fffbeb,stroke:#d97706,stroke-width:2px,stroke-dasharray: 4 4,color:#78350f;
    classDef aiStyle fill:#fdf4ff,stroke:#c026d3,stroke-width:2px,stroke-dasharray: 4 4,color:#701a75;
    classDef crossCutting fill:#faf5ff,stroke:#7c3aed,stroke-width:2px,color:#4c1d95;

    subgraph Tier1_Channels ["1. 接入与交互通道层 (Channels & Ingress)"]
        direction LR
        EndUsers["👤 终端用户 / IDE / 对话界面"]:::ingressStyle
        WebhookEvents["⚡ 外部自动化事件 / Webhook 触发"]:::ingressStyle
        IngressGateway["🛡️ 统一接入网关 (SSE/WebSocket 流式长连接)"]:::ingressStyle
    end

    subgraph Tier2_Routing ["2. 认知路由与意图分流层 (Cognitive Routing & Intent Triage)"]
        direction LR
        RuleEngine["⚙️ 确定性规则拦截 (快路径 System 1)"]:::routerStyle
        IntentClassifier["🧠 语义意图分类器 (轻量模型分流)"]:::routerStyle
    end

    subgraph Tier3_CoreAgent ["3. 核心 Agent 编排与状态域 (Agent Orchestration & State Core)"]
        direction TB
        subgraph OrchestrationBox ["规划调度与反思引擎 (Planner & Reflection Engine)"]
            StateGraph["确定性状态机 / Graph 调度器 (Max Steps 熔断)"]:::coreStyle
            NegativeLedger["失败反思账本 (Negative Ledger 防踩坑)"]:::coreStyle
        end

        subgraph ContextEngineBox ["上下文与记忆总线 (Context Engine)"]
            ContextPruning["动态上下文组装与修剪 (Pruning)"]:::coreStyle
            MemoryTier["分层记忆管理器 (Working / Episodic / Semantic)"]:::coreStyle
        end

        ToolGateway["语义工具调度网关 (Tool Execution Gateway & Schema Validator)"]:::coreStyle
    end

    subgraph Tier4_Execution ["4. 执行与存储基础设施 (Execution & State)"]
        direction TB
        CodeSandbox["📦 动态隔离代码沙箱池 (Docker / MicroVM 零外网出站)"]:::sandboxStyle
        EnterpriseAPIs["🏛️ 企业既有系统与核心数据资产 (via Anti-Corruption Layer)"]:::sandboxStyle
        VectorStorage["📚 向量与图知识库 (Vector DB / Graph RAG)"]:::sandboxStyle
    end

    subgraph Tier5_LLMGateway ["5. 模型中继与推理层 (LLM Inference Gateway)"]
        direction TB
        ModelAdapter["🌐 统一多模型适配器 (LiteLLM / vLLM / 跨云降级)"]:::aiStyle
        SemanticCache["⚡ 语义缓存 (Semantic Cache 防重复开销)"]:::aiStyle
        RateLimiter["⏱️ 动态速率限制与配额管控 (Rate Limiter)"]:::aiStyle
    end

    subgraph Tier_CrossCutting ["横切关注点守护底座 (Cross-Cutting Concerns)"]
        direction LR
        SecurityGuard["🛡️ 安全围栏: Prompt 注入检测 / PII 脱敏 / 权限拦截"]:::crossCutting
        HITLCenter["🧑‍⚖️ 人机协同: Human-in-the-loop (HITL) 审批与人工接管中心"]:::crossCutting
        TelemetryDashboard["📊 全链路观测: 步骤 TraceID / Token 成本仪表盘 / 认知轨迹评估"]:::crossCutting
    end

    %% 主干控制流与受控交互连线
    EndUsers -->|"1. 提交业务意图"| IngressGateway
    WebhookEvents -->|"1. 异步触发事件"| IngressGateway
    IngressGateway -->|"2. 意图分流分析"| Tier2_Routing
    RuleEngine -->|"3a. 快路径直接响应"| IngressGateway
    IntentClassifier -->|"3b. 激活复杂认知循环"| Tier3_CoreAgent

    StateGraph <-->|"动态组装与回溯"| ContextPruning
    StateGraph -->|"受控调用指令"| ToolGateway
    ToolGateway -->|"4. 隔离执行动态代码"| CodeSandbox
    ToolGateway -->|"5. 穿透访问外部业务"| EnterpriseAPIs
    ContextPruning <-->|"相似度检索召回"| VectorStorage

    Tier3_CoreAgent <-->|"6. 推理请求与 Tool Call 返回"| Tier5_LLMGateway
    Tier3_CoreAgent -.->|"高危写操作 / 失败挂起"| HITLCenter
    HITLCenter -.->|"人工审批放行 / 驳回决议"| Tier3_CoreAgent
    Tier_CrossCutting -.->|"横向安全过滤与遥测捕获"| Tier3_CoreAgent
```

---

## 2. 系统分层与信息流阐释 (Context & Information Flows)

1. **通道与接入层 (Channels & Ingress)**:
   - 终结外部客户端连接，提供统一身份凭证校验与支持分钟级保持的 WebSocket / SSE 流式通信管道。
2. **意图路由层 (Cognitive Routing)**:
   - 贯彻“快慢思考分级”原则：标准查询由规则引擎和轻量模型就近快速答复（毫秒级）；复杂未决推理才导入核心 Agent 编排域。
3. **Agent 编排与状态核心域 (State Core)**:
   - 由确定性状态机硬工程化推进，严守最大步数限制（Max Steps）以防死循环；
   - 动态上下文修剪模块（Context Pruner）负责剥离冗余堆栈与维护负向失败账本，杜绝 Token 浪费。
4. **受控执行与模型中继网关**:
   - 动态代码只能运行于零外网出站权限的独立沙箱（Tool Sandbox）；模型推理统一经由语义缓存与限流网关中继，消除跨云厂商锁定。
5. **横切安全与人机协同底座**:
   - 纵向覆盖 Prompt 注入防护、输入输出 PII 脱敏、全链路单步 TraceID 追踪以及关键节点专职审批人（HITL）拦截通道。

---

## 3. AOD 合格性“3 分钟压力测试”自检记录 (The 3-Minute Test)

- [x] **白板复述测试 (Whiteboard Test)**: 架构师可在 3 分钟内画出“接入 -> 意图分流 -> 状态与上下文编排 -> 沙箱/推理 -> 横切围栏”骨架，讲清快慢路径与死循环熔断。
- [x] **职责定位测试 (Responsibility Test)**: 抛出高危写操作场景，信息流清晰流经“意图路由 -> 状态编排 -> HITL审批挂起 -> 授权签字 -> 沙箱执行”，职责边界清晰无重叠。
- [x] **技术无关测试 (Technology Agnostic Test)**: 概念图中不包含任何具体框架或云厂商专有私有类，更换底层 LLM 或沙箱驱动无需重画。
- [x] **横切可见测试 (Cross-Cutting Test)**: 安全围栏 Guardrails、HITL 人机协同中心与全链路可观测性在横切层中均具有显式承载位置。
