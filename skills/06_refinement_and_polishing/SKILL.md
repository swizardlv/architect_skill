---
name: architecture-documentation-refinement
description: 对架构全景四层文档进行深度打磨与质量深化，消除粗糙与空洞内容，补充量化参数、异常处理、边界约束与技术选型论证。
---

# 架构文档深度打磨与质量深化技能 (Architecture Documentation Refinement)

## 技能定位与核心职责
初版生成的架构文档往往偏向框架结构和骨架概述，容易出现粗糙、表述笼统、缺少落地技术参数的问题。
本技能作为架构全生命周期中的**深度打磨（Polishing & Refinement）环节**，对系统全生命周期文档进行逐一深化与强化。

## 核心深化维度 (Refinement Dimensions)
1. **业务与需求层 (01-requirements)**:
   - 杜绝笼统叙述，必须具备清晰的量化商业 KPI、投资回报模型（ROI）；
   - 端到端用例必须包含主成功流、备选流、极端异常分支（Exception Paths）以及并发竞态应对；
   - 功能需求规约 (FR) 必须逐项具备输入、业务规则、算法逻辑、输出以及优先级。
2. **概念与逻辑层 (02-architecture-design)**:
   - 全面落地 Architecture Thinking 图谱 (AOD, CM, LM, DM, FSM, Sequence, DataFlow)；
   - 领域模型必须明确聚合根内聚范围、实体生命周期、值对象不可变性与数学级不变量定理；
   - 逻辑组件与物理微服务、容器、基础设施的映射关系必须完备。
3. **物理与工程层 (03-engineering-and-physics)**:
   - 物理拓扑必须具备具体节点规格（CPU/内存/NVMe/网络绑核/内核参数）、多机房专线时延 RTT、网络隔离区划；
   - 数据架构必须具备生产级 DDL、分区分表策略、冷热分层存储生命周期与 TTL 规则；
   - 容灾与韧性矩阵必须具备 FMEA 故障模式分析、混沌注入指令与 RTO/RPO 恢复指标；
   - ADR 决策记录必须包含被否决方案的详细对比与不得不承担的代价权衡。
4. **实施与组织层 (04-delivery-and-organization)**:
   - 康威定律组织拓扑必须具备明确的代码路径所有权矩阵（Code Ownership）；
   - WBS 估算必须具备故事点（SP）与人天（PD）推导逻辑；
   - 穿刺测试 (Tracer Bullet PoC) 规约必须具备可落地的验收断言。
