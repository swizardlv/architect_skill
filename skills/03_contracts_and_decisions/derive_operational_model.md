# Skill: derive_operational_model (运行模型 OM 建模器)

> 如果说 **AOD** 描绘了系统的全局轮廓，**CM** 解剖了系统的逻辑结构与组件边界，那么 **OM（Operational Model，运行模型）** 回答的就是最接地气也最硬核的问题：**“这些组件到底跑在哪里？如何保证它在真实物理世界中扛住流量、不宕机、合规且能容灾？”**
>
> 在 IBM Architecture Thinking 中，OM 是承接非功能性需求（NFRs / Quality Attributes）的最主要工件。它将 CM 中定义的软件构件映射到基础设施、网络分区与硬件节点上，直接决定了系统的性能（Performance）、可用性（Availability）、弹性（Scalability）与安全性（Security）。

---

## 1. OM 的核心结构：双层演进 (Logical OM -> Physical OM)

IBM 方法论严格要求 OM 经历从**逻辑执行环境**到**物理基础设施落地**的平滑演进，避免过早被特定云厂商或具体硬件型号所绑架：

```text
+-------------------------------------------------------------+
| 1. 逻辑运行模型 (Logical OM)                                 |
| 关注抽象执行环境、网络隔离与拓扑区域：                         |
| - 区域 (Zone): 互联网接入区 (DMZ)、应用计算区、核心数据区     |
| - 节点角色 (Node Role): 边缘网关节点、无状态微服务集群        |
| - 抽象连接: 跨区 TLS 双向互信通道、低延迟数据同步通道        |
+------------------------------+------------------------------+
                               | 选型与规格细化 (Realization)
                               v
+-------------------------------------------------------------+
| 2. 物理运行模型 (Physical OM)                                |
| 绑定具体数据中心、云服务机型、网络拓扑与软件配置：            |
| - 部署位置: AWS us-east-1 (跨 3 个 AZ) + 本地私有数据中心    |
| - 计算规格: EKS Node Group (c6i.2xlarge, 8c16g, 自动扩缩容)   |
| - 网络拓扑: VPC Peering, Transit Gateway, F5 BIG-IP, CIDR    |
| - 存储形态: Amazon Aurora PostgreSQL (Multi-AZ, 读写分离)    |
+-------------------------------------------------------------+
```

### 1.1 逻辑运行模型 (Logical OM)
- **节点角色 (Node Types / Execution Environments)**: 抽象出承载逻辑组件的运行时容器（如“边缘接入网关节点”、“单线程确定性撮合节点”、“高可用分布式总账节点”）。
- **安全区域 (Security Zones / Network Zones)**: 定义网络边界与信任等级（如 DMZ 外部接入区、内网应用计算区、核心数据持久化区、主权专线互联区）。
- **位置无关性 (Location Independence)**: 关注节点间的通信协议等级、延迟上限、带宽预算与隔离级别，暂不限定具体云厂商或物理机架。

### 1.2 物理运行模型 (Physical OM)
- **物理基础设施映射**: 标明具体的机房物理分布、可用区（AZ）、机架分布（Rack Distribution）或云厂商托管基础设施。
- **软硬件规格与容量规划 (Sizing)**: 标明具体的物理 CPU 核心数、内存大页分配量（HugePages）、磁盘阵列与 IOPS、网络网卡（如 Solarflare / SR-IOV）及带宽。
- **网络拓扑与安全落地**: 具体的 IP 网段分配（CIDR）、子网划分、路由表、物理交换机端口走线、防火墙与安全组规则、集群节点副本数。

---

## 2. 优秀 OM 的四大设计要求与核心视角

### 2.1 严格的拓扑分区与纵深防御 (Network & Security Zones)
- **明确系统安全防线**: 严禁外网流量直通核心数据区或底层数据库节点。
- **边界跳板与反向代理**: 外部请求必须终止在 DMZ 接入层，通过专用网络信道、白名单、双向 mTLS 加密或专线光纤穿透至核心计算区。

### 2.2 可用性与容灾拓扑 (HA & Disaster Recovery Topology)
- **RTO 与 RPO 强指标落实**: 清晰展现系统如何达成在 NFR 中承诺的 **RTO（恢复时间目标）** 与 **RPO（数据丢失目标）**。
- **部署模式可视化**: 明确是“同城双活（Active-Active）”、“两地三中心”还是“主备秒级热倒换（Hot Standby with Quorum）”。
- **故障域隔离 (Fault Domain Isolation)**: 清晰表达当单个机柜掉电、单个机房光纤中断甚至整可用区（AZ）失效时，流量如何自动重路由、数据如何防脑裂仲裁。

### 2.3 部署单元映射 (Deployment Mapping / Allocation)
- **CM 与 OM 的强纽带**: 物理 CM 中的每一个构建物（可执行文件、动态库、Pod、数据库表空间）都必须在 OM 中明确标注“部署在哪个具体节点/集群上”。
- **共存与隔离规则 (Colocation & Isolation Rules)**:
  - **低延迟共存**: 哪些构件为了微秒级 IPC 必须同机甚至同 NUMA 节点部署。
  - **安全与资源隔离**: 哪些构件出于安全沙箱或防 CPU 抢占考虑，必须独占物理隔离节点部署。

### 2.4 容量规划与伸缩策略 (Capacity Sizing & Elasticity)
- **基线容量与峰值冗余**: 基于业务 TPS、QPS 及日增数据量，推导计算核心、内存缓存及存储的容量基线。
- **伸缩边界与指标**: 明确横向扩缩容策略（HPA / 静态预留），标明伸缩触发指标（如 CPU > 70%、RingBuffer 积压阈值）。

---

## 3. Agent AI 时代的运行模型重构 (Physical OM Paradigm Shift)

OM 是 Agent 时代发生**物理形变最大**的架构工件。Agent 系统从纯通用微服务集群演进为**包含边缘防御、CPU 业务编排、异构 GPU 推理池与高危沙箱隔离区**的复合拓扑：

```
[ 外部互联网 / 客户端 ]
          │ (HTTPS / WSS)
          ▼
[ 边缘接入区 DMZ: API Gateway & Guardrail WAF ] ────► 执行 Prompt 注入实时过滤
          │
          ▼
[ 核心业务计算区 (K8s / CPU Nodes) ]
  • Agent 编排服务集群 (Stateless Pods, 配置 HPA)
  • 语义缓存与状态服务 (Redis Enterprise / Valkey 集群)
  • 记忆检索层 (pgvector / Qdrant 向量计算节点)
          │
          ├─────────────────────────────────────────┐
          │ (受控 mTLS 专线)                        │ (严格隔离 RPC 管道)
          ▼                                         ▼
[ 独立推理区 (GPU Serving Nodes) ]       [ 动态计算沙箱隔离区 (Sandbox Zone) ]
  • vLLM / TensorRT-LLM 集群              • 极简微虚机 / 安全容器 (Firecracker / gVisor)
  • 裸金属/GPU 节点 (A100/H100/L40S)       • 运行 Agent 动态生成的 Bash / Python 代码
  • 专用 RoCE / InfiniBand 低延迟互联     • 零公网出站权限、瞬时销毁、文件系统写透即弃
```

### 3.1 三大核心物理环境新要求
1. **隔离执行沙箱区 (Isolated Execution Sandbox Zone)**:
   - **物理形态**: 严禁在业务宿主机或主 K8s 集群中直接运行 Agent 生成的动态代码。必须采用基于 MicroVM（如 AWS Firecracker、Kata Containers）或轻量级安全容器（如 gVisor、E2B）的专用沙箱池。
   - **网络与存储策略**: 沙箱施加**严格的出站网络限制（Egress Network Policy）**，默认断开公网出站，文件系统写透即弃（Ephemeral Filesystem），秒级销毁重建。
2. **异构算力与显存规划 (Heterogeneous Sizing)**:
   - 明确物理划分 **CPU 逻辑编排节点** 与 **GPU 模型推理节点**。
   - 自建模型推理节点需针对 GPU 显存带宽、持续批处理调度器（Continuous Batching）以及 OOM 显存耗尽时的主机队列背压制定硬指标。
3. **长连接与流式通道规划 (Streaming Infrastructure)**:
   - Agent 单轮复杂推理耗时达数秒至数十秒，传统短连接易频繁超时。OM 必须全面升级为**支持 WebSocket / HTTP-2 SSE 流式传输的长连接网关拓扑**，Keep-Alive 超时时间从秒级放宽至分钟级，并配备断线无损恢复机制（Resume Stream）。

### 3.2 Agent OM 三维评判标准 (Evaluation Criteria)
- **逃逸防御拓扑测试 (Escape Containment Test)**: 当 Agent 在沙箱内执行高危指令（如 `rm -rf /`、网络端口扫描或异常加密脚本）时，物理网络与安全隔离机制能否在秒级销毁容器且完全不波及相邻主机？
- **长连接雪崩与重连风暴评估 (Streaming Storm Resilience)**: 千级并发流式请求时，网关的并发连接数配额、文件描述符与内存开销是否经过测算？断线重连是否有防雪崩退避？
- **冷启动与弹性伸缩时延 (Cold Start Sizing)**: 沙箱分配与弹性容器的冷启动延迟是否控制在数百毫秒以内？严禁因沙箱环境初始化过慢拖垮交互响应。

---

## 4. 经典交付物规范：节点规范卡片 (Node Specification)

每个核心计算节点、存储节点或集群必须配有一张标准节点规范卡片：

| 规范要素 | 填写内容示例 | 架构约束与审查点 |
| :--- | :--- | :--- |
| **节点标识** | `NODE-CORE-01: 核心撮合计算节点 (Core Matching Node)` | 明确节点角色与集群命名 |
| **承载组件 (CM 映射)** | `matching-core.so`, `orderbook-engine` (来自物理 CM) | 建立与 CM 构建物的直接映射 |
| **网络区域归属** | 内部专用核心区 (Zone 0 - Private Core Network) | 明确其所在的物理子网与安全级别 |
| **硬件/实例规格** | Dell PowerEdge R760, 双路 AMD EPYC 9654 (192核), 64GB 巨页 | 标明 CPU 独占绑核、内存巨页与 NUMA 配置 |
| **可用性设计** | 同城双活双机配置 (Active / Hot-Standby)，跨独立供电机架 | 标明故障域隔离与 RPO/RTO 机制 |
| **网络与交互策略** | 仅接收定序器 SPSC 环推流；输出仅允许直推行情与落盘守护 | 最小网络权限与通信协议约束 |
| **存储与持久化** | 本地直通 PCIe 5.0 NVMe SSD 阵列，开启 O_DIRECT 异步刷盘 | 约束存储介质、挂载点与落盘行为 |

---

## 5. 检验 OM 是否合格的“四大压力实战测试”

在评审会前，架构师必须通过以下实战场景自检：

1. **拔电源测试 (Chaos / Failure Scenario Test)**:
   - 架构师在 OM 图上圈死一个机房、一台核心主服务器或一条光纤专线，推演接下来的 30 秒内：心跳如何感知、流量如何切换、数据状态机如何防脑裂？
2. **容量与成本测试 (Cost & Sizing Walkthrough)**:
   - 将 OM 上的硬件机型、CPU/内存/GPU 显卡配额与专线拉取清单，财务与 SRE 团队能否据此直接计算出年度基础设施预算（CAPEX / OPEX）？
3. **运维与可观测测试 (Operational Readiness)**:
   - 运维团队查看该图，能否一眼看出监控探针（Agent）、日志收集器（Log Shipper）、硬件时钟网卡应挂载在哪些节点与网络通道上？
4. **沙箱逃逸与长连接抗压测试 (Sandbox & Streaming Test)**:
   - 推演沙箱失控容器秒级销毁与千万级 Token 吞吐下长连接网关内存稳定性，验证网络隔离与冷启动指标达标。
