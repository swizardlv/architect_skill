# Skill: derive_component_model (组件模型 CM 建模器)

> 如果说 **AOD** 是系统的“鸟瞰全景图”，那么 **CM（Component Model，组件模型）** 就是系统内部结构的“工程解剖图”。在 IBM Architecture Thinking 中，CM 是承接 AOD、指导下游工程实施最核心的工件。它的核心目标是：**定义系统由哪些独立的逻辑单元（组件）构成、每个组件承担什么职责（Responsibilities）、通过什么接口（Interfaces）对外暴露能力，以及组件之间如何协作（Interactions）。**

---

## 1. CM 的核心结构：双层演进 (Logical CM -> Physical CM)

IBM 方法论严格要求 CM 经历从**逻辑设计**到**物理实现**的平滑演进，避免一开始就掉入代码框架与中间件的细节泥潭：

```text
+-------------------------------------------------------------+
| 1. 逻辑组件模型 (Logical CM)                                 |
| 抽象技术栈，聚焦业务边界：                                    |
| Component: 订单履约组件 (Order Fulfillment)                   |
| - 职责: 状态机驱动、履约分解、逆向取消调度                   |
| - 提供的接口: IOrderFulfillmentService (create, cancel)      |
| - 依赖的接口: IInventoryReservationService, IPaymentQuery   |
+------------------------------+------------------------------+
                               | 映射 (Mapping & Realization)
                               v
+-------------------------------------------------------------+
| 2. 物理组件模型 (Physical CM)                                |
| 绑定具体技术实现与运行时构件：                                |
| Component: order-fulfillment-service.jar (Spring Boot 微服务) |
| - 物理接口: gRPC (Protobuf v3), REST/JSON                   |
| - 存储依赖: PostgreSQL 16 (私有 Schema), Redis 集群         |
| - 消息交互: Kafka Topic: "order.events.v1"                  |
+-------------------------------------------------------------+
```

### 1.1 逻辑组件模型 (Logical CM)
- **技术无关**: 与具体编程语言、执行框架无关。
- **职责与契约为纲**: 严格按照领域边界划分组件，明确标定：
  - **组件职责 (Responsibilities)**: 核心业务能力定义。
  - **提供的接口 (Provided Interfaces)**: 对外暴露的业务接口签名（方法名、入参、出参）。
  - **依赖的接口 (Required Interfaces)**: 正常工作所必须调用的上游接口。

### 1.2 物理组件模型 (Physical CM)
- **逻辑组件的具体技术实例化**:
  - 明确组件的技术形态（如微服务独立部署包、共享动态库、Serverless Function、存储引擎表集合等）。
  - 明确具体的物理通信协议与数据格式（如 SBE 二进制、gRPC/Protobuf、REST/JSON、Kafka Avro）。

---

## 2. 优秀 CM 的四大核心设计要求

### 2.1 高内聚、松耦合 (High Cohesion & Loose Coupling)
- **单一职责原则 (Single Responsibility)**: 每个组件有且仅有一个引起它变化的原因。例如，将“计费规则计算”与“账单渲染导出”拆分为两个不同组件。
- **无环依赖原则 (Acyclic Dependencies Principle, ADP)**: 组件之间的依赖拓扑图必须是**有向无环图 (DAG)**。若组件 A 依赖 B，B 依赖 C，C 又调回 A，说明边界切分错误，必须引入事件总线 (Event/Pub-Sub) 或通过依赖倒置接口进行解耦。

### 2.2 契约优先 (Contract-First / Interface-Centric)
- 严禁只在图上画方框和双向箭头。
- 任何连线都必须指明：
  - **Provided Interface (提供的接口)**: 该组件为外部暴露的白盒能力。
  - **Required Interface (依赖的接口)**: 该组件运行所必需调用的外部能力。
- **严禁私有穿透**: 严禁组件直接跨过边界读写另一个组件的私有数据库或内部数据结构。

### 2.3 动态交互闭环 (Static View + Dynamic View)
- **静态必须有动态支撑**: 针对系统核心的 3~5 个重大架构场景，必须给出对应的**组件时序图 (Component Sequence Diagram)**。
- **时序校验接口合理性**: 如果某个接口从未在任何时序图中被调用，说明该接口是多余冗余的；如果在时序图中出现了静态模型未定义的调用，说明组件接口定义缺失。

### 2.4 严格的数据归属权 (Data Ownership)
- **排他性所有权**: 每个组件对其负责持久化和状态管理的领域数据拥有绝对的排他权。
- 明确标注每个业务实体属于哪个核心组件负责维护，杜绝多组件并发直接读写共享存储。

---

## 3. 标准交付物：组件规范卡片 (Component Specification)

每个关键组件都必须具备一份标准组件规范卡片：

| 规范要素 | 填写内容示例 | 架构约束与审查点 |
| :--- | :--- | :--- |
| **组件标识** | `COMP-03: 风险评估引擎 (Risk Evaluation Engine)` | 命名清晰，体现业务领域属性 |
| **组件类型** | 核心业务组件（内部构建） | 区分自研、商业现成套件（COTS）或第三方托管 |
| **核心职责** | 实时拦截交易请求，根据评分卡及规则引擎计算欺诈概率 | 3~5 句话精炼概括，不可跨界侵入其他域 |
| **提供接口 (Provided)** | `IRiskAssessmentService` (API: `evaluateTransaction`) | 具备明确的方法名、输入参数、返回结构 |
| **依赖接口 (Required)** | `IUserHistoricalProfile`, `IDeviceFingerprint` | 明确依赖的上游能力与调用容错预期（超时/降级） |
| **质量属性/NFR 要求** | P99 响应时间 ≤ 15ms；高可用 99.99%；必须无状态 | 约束物理落地时的部署与并发要求 |
| **物理技术映射** | C++ 独占绑核动态库 / gRPC 微服务，无本地状态 | 逻辑模型向物理模型的落地绑定 |
| **数据资产所有权** | 独占管理 `RiskRuleSet` 与 `AccountRiskState` | 明确排他性数据归属，严禁外部直接修改 |

---

## 4. 检验 CM 是否合格的“三道防线”

在架构交付评审前，必须通过以下“三道防线”自检：

1. **外包/团队分配测试 (Team Allocation Test)**:
   - 若将这套 CM 分解为不同组件交付物交给不同的敏捷小组或外包团队开发，各小组能否仅凭**组件职责与接口契约**独立启动编码，而无需频繁开会同步内部实现细节？
2. **变更隔离测试 (Change Impact Test)**:
   - 假设某一组件内部的业务逻辑或存储方案发生重大重构（如算法优化或数据库换型），其他组件是否完全不被波及？若改动一个组件导致全链路接口发生级联修改，说明边界切分失败。
3. **OM 衔接测试 (Operational Readiness Test)**:
   - 拿到物理 CM 后，运维与基础设施架构师（SRE）能否据此清晰推导其所需的容器实例规模、CPU/内存配置、网络拓扑与存储分级？若无法推导，说明物理 CM 缺失运行时关键特征。
