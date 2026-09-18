# 架构概念验证原型设计与结项报告 (PoC Charter & Final Report)

> **架构视角**: 架构深水区工程验证 (Empirical Spike & Architecture Verification)  
> **核心使命**: 秉持“极窄深度（Tracer Bullet）、用完即弃（Disposable）、量化裁判（Empirical Referee）”原则，通过拟真物理环境与破坏性混沌实验，刺破高风险技术假设，以客观数据终结 ADR 争执并校准 CM/OM 规格。

---

## 1. PoC 任务卡片与立项基准 (PoC Charter)

| 规范要素 | 规格内容与定义说明 |
| :--- | :--- |
| **PoC 标识与名称** | `POC-001: {验证核心对象与极端条件，如：高并发无锁撮合核心在极端网络抖动下的延迟与状态恢复}` |
| **驱动的架构决策 (ADR)** | 关联 [`ADR-00X: {决策名称}`](file:///path/to/adr.md) |
| **关联的架构需求 (ARC)** | 关联 [`ARC-PERF-01: {量化指标}`](file:///path/to/arc.md), `ARC-AVAIL-01` |
| **承接的 ATAM 风险项** | 承接 [`SCEN-01 / RISK-01: {高风险场景简述}`](file:///path/to/utility-tree-atam.md) |
| **验证周期与资源预算** | **严格时间盒**: {如：1 周 (5 个工作日)}；资源配置: {如：2 名架构/资深开发，3 台独立物理机/测试实例} |
| **垂直切片定位 (Spike)** | **窄而深垂直切片 (Tracer Bullet)**：贯穿从客户端输入网关到内存处理、再到持久化定序落盘单条完整链路，剥离 95% 无关业务代码。 |

---

## 2. 垂直切片链路拓扑 (Tracer Bullet Architecture Flow)

```mermaid
flowchart LR
    %% 样式表定义
    classDef clientStyle fill:#f8fafc,stroke:#64748b,stroke-width:1px,color:#1e293b;
    classDef compStyle fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;
    classDef storeStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef chaosStyle fill:#fef2f2,stroke:#dc2626,stroke-width:2px,stroke-dasharray: 3 3,color:#991b1b;

    Client["压力生成器 (Gatling / JMeter 拟真报文)"]:::clientStyle
    Gateway["切片接入节点 (Ingress / 网关)"]:::compStyle
    Core["被测核心计算引擎 (CM 核心构件)"]:::compStyle
    Ledger["异步持久化 / 备机复制节点 (OM 物理节点)"]:::storeStyle
    Chaos["💥 混沌注入源 (延迟/丢包/kill -9)"]:::chaosStyle

    Client -->|"注入极限并发负载"| Gateway
    Gateway -->|"二进制内存分发"| Core
    Core -->|"定序日志流复制"| Ledger
    Chaos -.->|"注入网络丢包与主板断电"| Core
    Chaos -.->|"注入 50ms 网络延迟"| Ledger
```

---

## 3. 预设量化验收指标与熔断红线 (Success & Kill Criteria)

| 验证维度 | 预设通过验收门槛 (Success Criteria) | 预设不可篡改的熔断淘汰指标 (Kill Criteria) |
| :--- | :--- | :--- |
| **吞吐能力 (Throughput)** | 稳态吞吐 $\ge$ {如：50,000 TPS} | 压测吞吐跌落超过 {如：40%}，即刻判定方案淘汰 |
| **延迟分位 (Latency)** | P99 延迟 $\le$ {如：150μs}，P999 延迟 $\le$ {如：500μs} | P99 延迟突增突破 {如：2.0ms} 或发生超过 50ms 的长停顿，直接熔断 |
| **状态一致性 (Consistency)** | 故障恢复后账本核对 100% 逐位一致，差错率 = 0 | 发生任何单边账、超卖、不可逆数据覆盖，直接判定否决 |
| **故障转移恢复 (Failover)** | 主节点故障下线，备机接管时间 RTO $\le$ {如：1.5s} | 节点切换时间超出 {如：5.0s} 或发生双主脑裂双写，判定淘汰 |

---

## 4. 实验环境与破坏性实验执行 (Chaos & Experimental Execution)

### 4.1 物理测试环境配置 (True Physics Environment)
- **计算节点拓扑**: {明确说明 3~4 台物理节点规格，如：Intel Xeon 16C, 64GB RAM, 独占物理网卡}
- **拟真网络拓扑**: 通过 Linux `tc / netem` 配置跨可用区 50ms 网络延迟与 1% 随机丢包率，拒绝 localhost 玩具环境。
- **拟真测试数据集**: 注入 1,000,000 笔真实业务脱敏与边界异常混合数据流（覆盖乱序、超长、空值）。

### 4.2 破坏性混沌实验过程记录 (Breaking the System)
1. **实验 1: 极限并发加压与性能拐点测试**
   - 从 10,000 TPS 阶梯式递增至 80,000 TPS，持续寻找系统从线性增长到排队队列击穿的极限拐点。
2. **实验 2: 跨区网络抖动与断流实验**
   - 在峰值状态下注入 100ms 网络延迟抖动，持续 30 秒，观测内存缓冲区占用与背压机制。
3. **实验 3: 核心进程强杀与自愈实验**
   - 在高并发写入期间使用 `kill -9` 强杀 Primary 核心进程，观测备用节点的接管秒表与数据回放。

---

## 5. 实验观测数据与实测结果 (Empirical Observations)

```
[实测性能阶梯响应曲线 (Throughput vs Latency)]
TPS        Latency P99     CPU Load      GC / Pause       状态
10,000     45μs            18%           0 ms             平稳
30,000     78μs            42%           0 ms             平稳
50,000     112μs           68%           0 ms             达标 (验收通过)
65,000     145μs           84%           0 ms             极限拐点
75,000     890μs           98%           4.2 ms (排队抖动)  过载保护触发
```

- **压测实测数据**:
  - 峰值稳态达到 `{实测 TPS}`，核心 P99 延迟为 `{实测延迟}`，未触发熔断红线。
- **故障注入破损点观测**:
  - 在注入 100ms 网络延迟时，发现内存缓冲区水位由 15% 快速上升至 78%，证明原设计的无界缓冲区存在 OOM 隐患，需要补齐有界背压防护。
- **故障转移与恢复实测**:
  - 强杀主节点后，备机在 `{实测 RTO 秒数}` 内完成日志重放与接管，状态对账逐位一致。

---

## 6. 最终决议与架构闭环落地行动 (Resolution & 100% Feedback Loop)

### 6.1 评审结项最终决议
- **决议结果**: **【条件性采纳 (Conditionally Accepted)】** / **【正式采纳 (Accepted)】** / **【否决淘汰 (Rejected)】**
- **决议说明**: 核心低延迟与高吞吐假设得到真实物理数据证实，但在抗网络抖动与缓冲区管理上暴露了架构薄弱点，必须通过闭环补强后方可进入正式研发。

### 6.2 架构资产反哺闭环清单 (Feedback Actions)

| 闭环受体工件 | 变更类型 | 调整内容与设计补齐 | 闭环状态 |
| :--- | :--- | :--- | :--- |
| **组件模型 (CM)** | 结构补齐 | 在 `COMP-01 Ingress` 与核心组件之间补上有界环形缓冲区与背压丢弃组件 | **已完成修改** |
| **运行模型 (OM)** | 规格校准 | 根据实测内存占用，将核心节点的内存配额从 32GB 上调至 64GB，增加预留缓冲 | **已完成校准** |
| **架构决策 (ADR)**| 状态演进 | [`ADR-00X`](file:///path/to/adr.md) 状态由 `Proposed` 变更为 `Accepted`，并将 PoC 压测图表归档作为决策证据 | **已完成签署** |
| **代码处理** | 用完即弃 | 声明 PoC 探索性代码按规约废弃，仅保留基准自动化测试用例 `tests/benchmark/` | **已规约归档** |
