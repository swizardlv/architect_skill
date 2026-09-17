# 运行模型说明书 (Operational Model - OM Template)

> 本文档遵循 IBM Team Solution Design 与 Architecture Thinking 规范，作为承接非功能性需求（NFRs）与 CM 物理组件的运行基础设施架构工件。

---

## 1. 逻辑运行模型 (Logical Operational Model - Logical OM)

```mermaid
flowchart TB
    %% 样式定义
    classDef dmzStyle fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef appStyle fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;
    classDef dataStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef extStyle fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4,color:#1e293b;

    subgraph LogicalDMZ ["【安全区域 1】边缘接入与网络隔离区 (DMZ Zone)"]
        direction LR
        IngressNodes["边缘接入与协议网关节点群<br/>[承载: 接入适配组件 COMP-01]"]:::dmzStyle
    end

    subgraph LogicalAppZone ["【安全区域 2】内部应用与核心计算区 (Private App Zone)"]
        direction TB
        CoreComputeNodes["核心业务与规则计算节点群<br/>[承载: COMP-02, COMP-03, COMP-04]"]:::appStyle
    end

    subgraph LogicalDataZone ["【安全区域 3】持久化数据与状态总账区 (Data & Ledger Zone)"]
        direction LR
        LedgerNodes["不可变持久化账本节点群<br/>[承载: 账本与快照组件 COMP-06]"]:::dataStyle
    end

    subgraph ExternalZone ["【外部区域】三方机构与主权专线互联区 (External / Partner Zone)"]
        direction TB
        PartnerGateways["外部合作方通道 / 监管接入终端"]:::extStyle
    end

    PartnerGateways -->|"mTLS 1.3 专线加密"| IngressNodes
    IngressNodes -->|"内部低延迟受控信道"| CoreComputeNodes
    CoreComputeNodes <-->|"不可变写入与状态同步"| LedgerNodes
```

---

## 2. 物理运行模型 (Physical Operational Model - Physical OM)

```mermaid
flowchart TB
    %% 物理拓扑样式
    classDef dcAStyle fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;
    classDef dcBStyle fill:#faf5ff,stroke:#7c3aed,stroke-width:2px,color:#4c1d95;
    classDef witnessStyle fill:#fefce8,stroke:#ca8a04,stroke-width:2px,color:#713f12;

    subgraph PrimarySite ["生产主数据中心 (Primary DC - Zone A)"]
        subgraph RackA1 ["机架 A-01 (双路供电)"]
            NodeGW_A["物理主机 01: 网关与前置网卡 (Dell R760)"]:::dcAStyle
            NodeCore_A["物理主机 02: 撮合计算主核心 (独占绑核)"]:::dcAStyle
            Storage_A["直通 NVMe PCIe 5.0 SSD 阵列"]:::dcAStyle
        end
    end

    subgraph SecondarySite ["同城同构备用数据中心 (Secondary DC - Zone B)"]
        subgraph RackB1 ["机架 B-01 (独立变电站)"]
            NodeGW_B["物理主机 03: 备用接入网关"]:::dcBStyle
            NodeCore_B["物理主机 04: 镜像只读重放核心"]:::dcBStyle
            Storage_B["备用 NVMe 存储阵列"]:::dcBStyle
        end
    end

    subgraph WitnessSite ["独立第三仲裁站点 (Quorum Witness)"]
        Arbitrator["硬件仲裁哨兵 (Witness Node)"]:::witnessStyle
    end

    NodeGW_A --> NodeCore_A --> Storage_A
    NodeCore_A ==>|"同城专用低时延裸光纤 (DWDM ≤ 250µs)"| NodeCore_B
    NodeCore_A -.->|"心跳租约保持 (50ms)"| Arbitrator
    NodeCore_B -.->|"心跳租约监测 (50ms)"| Arbitrator
```

---

## 3. 核心节点规范卡片集 (Node Specifications)

### 3.1 NODE-01: 核心计算节点 (Core Compute Node)
| 规范要素 | 架构内容说明 |
| :--- | :--- |
| **节点标识** | `NODE-CORE-01: 主撮合与定序核心主机` |
| **承载组件 (CM 映射)** | `matching-core.so`, `sequencer-hub` (物理 CM) |
| **网络区域归属** | 私有核心计算区 (Zone 0 - Private Isolated VLAN) |
| **硬件/实例规格** | Dell PowerEdge R760, 2x AMD EPYC 9654, 64GB 1GB 巨页内存, NUMA Node 0 锁定 |
| **可用性设计** | 主备热倒换 (Active-Standby)，跨独立供电机架与同城双机房配置 |
| **网络与交互策略** | 仅接收网关 SPSC 环推流，输出仅允许直连组播交换机与 WAL 存储 |
| **存储与持久化** | 本地直通 PCIe 5.0 NVMe SSD，开启 O_DIRECT 异步无锁追加写 |

---

## 4. CM 构件部署映射与隔离规则矩阵 (Deployment Allocation Matrix)

| 物理 CM 构件名称 | 目标运行物理节点 | 部署形态 (Process/Container) | 共存与隔离规则 (Colocation/Isolation) |
| :--- | :--- | :--- | :--- |
| `ingress-gateway` | `NODE-GW-01` (Core 0) | 用户态独占进程 | 必须与网卡物理端口直连，禁止跨 CPU Socket |
| `matching-core` | `NODE-CORE-01` (Core 2) | 单线程独占动态库 | 必须独占 CPU 物理核，完全禁止其他线程抢占 |
| `market-broadcaster`| `NODE-CORE-01` (Core 3) | 组播推流独立进程 | 共享同一 NUMA 节点的共享内存以达成微秒级事件获取 |
| `wal-daemon` | `NODE-CORE-01` (Core 4) | 异步写盘守护进程 | 独立绑核，隔离磁盘 I/O 中断对撮合核心的干扰 |

---

## 5. 容量规划与伸缩策略 (Capacity Sizing & Scalability)

- **吞吐与容量基线**: 测算基于单标的峰值 1,500,000 TPS 计算，每秒产生约 144MB 二进制事件流。
- **存储年化规划**: 8小时高频交易日产生约 4.1TB 日志，经异步压缩归档后需要 1.2TB/天冷存储容量。
- **伸缩边界**: 核心交易对采用静态独占物理分区（Static Core Sharding）；边缘接入层支持基于会话数的动态横向扩展。

---

## 6. OM 压力实战测试验证记录 (Stress & Failure Walkthrough)

- [ ] **拔电源测试 (Chaos / Failure Scenario Test)**:
  - 模拟主机掉电演练：主节点心跳中断超 250ms，独立第三机房仲裁哨兵自动收回租约，备机在 350ms 内平滑接管，达成 **RPO=0, RTO < 500ms**。(合格)
- [ ] **容量与成本测试 (Cost & Sizing Walkthrough)**:
  - 基于本 OM 清单拉取机房机柜、裸光纤租赁与物理机采购清单，SRE 与财务团队能够据此直接核算出年度 CAPEX/OPEX 基础设施预算。(合格)
- [ ] **运维与可观测测试 (Operational Readiness)**:
  - PTP 硬件时钟对齐探针、Prometheus Metrics 导出器与网络交换机镜像监控端口均在 OM 中唯一定位，SRE 无需额外猜测部署位置。(合格)
