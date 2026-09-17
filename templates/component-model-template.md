# 组件模型说明书 (Component Model - CM Template)

> 本文档遵循 IBM Team Solution Design 与 Architecture Thinking 规范，作为承接 AOD 全景概览图、指导下游团队工程实现的核心架构解剖工件。

---

## 1. 逻辑组件模型 (Logical Component Model - Logical CM)

```mermaid
flowchart TD
    %% 样式表定义
    classDef logicalComp fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;
    classDef interfaceNode fill:#ffffff,stroke:#0284c7,stroke-width:1px,stroke-dasharray: 2 2,color:#0369a1;

    subgraph LayerIngress ["接入层组件 (Ingress Tier)"]
        CompGateway["COMP-01: 接入适配组件<br/>(Ingress Adapter)"]:::logicalComp
    end

    subgraph LayerCore ["核心能力层组件 (Core Domain Tier)"]
        direction TB
        CompRisk["COMP-02: 实时风控组件<br/>(Risk Filter)"]:::logicalComp
        CompSeq["COMP-03: 仲裁定序组件<br/>(Sequencer Engine)"]:::logicalComp
        CompMatch["COMP-04: 业务撮合核心组件<br/>(Matching Core)"]:::logicalComp
    end

    subgraph LayerEgress ["分发与持久化组件 (Egress Tier)"]
        CompDispatch["COMP-05: 事件分发组件<br/>(Event Dispatcher)"]:::logicalComp
        CompLedger["COMP-06: 账本持久化组件<br/>(Ledger Store)"]:::logicalComp
    end

    %% 接口暴露与依赖连线 (无环有向图 DAG)
    CompGateway -->|"依赖: IRiskValidation"| CompRisk
    CompRisk -->|"依赖: ISequenceAllocation"| CompSeq
    CompSeq -->|"依赖: IExecutionSubmit"| CompMatch
    CompMatch -->|"依赖: IEventPublish"| CompDispatch
    CompDispatch -->|"依赖: ILedgerAppend"| CompLedger
```

---

## 2. 物理组件模型 (Physical Component Model - Physical CM)

```mermaid
flowchart TD
    %% 物理构件样式
    classDef binPkg fill:#f8fafc,stroke:#334155,stroke-width:2px,color:#0f172a;
    classDef storagePkg fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef protocolLink fill:#ffffff,stroke:#64748b,stroke-width:1px,color:#475569;

    subgraph PhysicalArtifacts ["运行时部署构件 (Physical Deployment Packages)"]
        PkgGW["ingress-gateway (用户态可执行文件)<br/>[协议: EF_VI / SBE Binary]"]:::binPkg
        PkgCore["matching-core.so (C++ 独占绑核动态库)<br/>[通信: 无锁 SPSC RingBuffer]"]:::binPkg
        PkgEgress["market-broadcaster (独立守护进程)<br/>[协议: UDP Multicast / ITCH 5.0]"]:::binPkg
        PkgStorage["ledger-daemon (直接I/O落盘进程)<br/>[存储: NVMe O_DIRECT WAL]"]:::storagePkg
    end

    PkgGW ==>|"SPSC 内存环形总线"| PkgCore
    PkgCore ==>|"事件输出总线"| PkgEgress
    PkgCore ==>|"直接 I/O 环形写入"| PkgStorage
```

---

## 3. 核心组件规范卡片集 (Component Specifications)

### 3.1 COMP-01: 接入适配组件 (Ingress Adapter)
| 规范要素 | 内容说明 |
| :--- | :--- |
| **组件标识** | `COMP-01: Ingress Adapter` |
| **组件类型** | 边界通信组件（自研） |
| **核心职责** | 终结网络连接，解析客户端报文，完成防重放时间戳校验 |
| **提供接口 (Provided)**| `IIngressSession (connect, disconnect, receivePacket)` |
| **依赖接口 (Required)**| `IRiskValidation (validateOrder), ISequenceAllocation (submitOrder)` |
| **质量属性/NFR 要求** | 单包反序列化延迟 ≤ 300ns；吞吐量 ≥ 2,000,000 ops/s；无锁设计 |
| **数据所有权 (Ownership)**| 独占管理外部会话连接描述符表与会话状态 |
| **物理技术映射** | C++ 纯轮询用户态驱动进程，通过连续定长内存池分配报文 |

---

## 4. 核心架构场景动态时序验证 (Component Sequence Diagrams)

### 场景一：常规业务黄金调用链路 (Happy Path)
```mermaid
sequenceDiagram
    autonumber
    participant GW as COMP-01: Ingress
    participant Risk as COMP-02: Risk
    participant Seq as COMP-03: Sequencer
    participant Core as COMP-04: Matching Core
    participant Dispatch as COMP-05: Dispatcher

    GW->>Risk: validateOrder(OrderRequest)
    Risk-->>GW: ValidationResult(Approved)
    GW->>Seq: submitOrder(OrderRequest)
    Seq->>Core: executeOrder(SequencedOrder)
    Core->>Dispatch: publishTradeEvents(ExecutionReport)
    Dispatch-->>GW: notifyClient(Receipt)
```

---

## 5. 领域数据所有权归属矩阵 (Data Ownership Matrix)

| 业务数据实体 / 资产 | 独占写入组件 (Exclusive Owner) | 只读消费组件 (Read-Only Consumers) | 持久化与存储模式 |
| :--- | :--- | :--- | :--- |
| **AccountBalance (账户资金)** | COMP-02: 实时风控组件 | Ingress, Admin | 内存预扣表 + WAL 镜像 |
| **OrderBookDepth (盘口深度)** | COMP-04: 撮合核心组件 | Dispatcher, MarketBroadcaster | 纯内存红黑树与双向链表 |
| **ClearingAuditLog (审计日志)** | COMP-06: 账本持久化组件 | External Audit, Analytics | NVMe 追加写日志文件 |

---

## 6. CM 合格性“三道防线”评审自检记录

- [ ] **防线一：外包/团队分配测试 (Team Allocation Test)**: 敏捷团队能否仅凭规范卡片中的 `Provided/Required` 接口独立开发？(合格)
- [ ] **防线二：变更隔离测试 (Change Impact Test)**: 内部算法或存储重构是否不波及其他组件接口？(合格)
- [ ] **防线三：OM 衔接测试 (Operational Readiness Test)**: SRE 能否依据物理 CM 直接推导部署拓扑与资源配置？(合格)
