---
name: architecture-overview
description: "Use when synthesizing architecture overview diagrams (AOD), defining system context boundaries, selecting architectural styles, or presenting high-level system structures to stakeholders"
---

# Architecture Overview (架构概览与系统全景)

## 概述

架构概览图（AOD, Architecture Overview Diagram）是连接商业意图与工程落地的顶层宏观蓝图。它负责向业务方、管理层与工程团队传达系统的整体轮廓、核心职责分层与关键数据流转方向。

在 AI / Agent 时代，AOD 摆脱了传统简单的 Web-App-DB 三层划分，必须清晰体现**接入层、认知控制平面、安全护栏、上下文生命周期管理与外部执行工具网关**。

## 适用场景 (When to Use)

- 系统启动阶段确立软硬件与三方边界（System Context）；
- 向跨职能团队或 ARB 委员会展示系统全局拓扑分层；
- 评估系统架构风格（如事件驱动、管道过滤器、分层单体还是微服务编排）并进行决策；
- 为后续组件模型（CM）与运行模型（OM）确立顶层骨架。

## 核心交付物与模板

1. **系统上下文图 (System Context)**：[system-context-template.md](templates/system-context-template.md)
2. **架构概览图 (AOD 图纸与叙述)**：[aod-template.md](templates/aod-template.md) 与 [aod-narrative-template.md](templates/aod-narrative-template.md)
3. **架构风格选型决策**：[architectural-style-selection-template.md](templates/architectural-style-selection-template.md)

## AOD 在 AI 时代的新结构分层

工业级 AI/Agent 系统的 AOD 推荐采用以下五层经典分层：

```
+-----------------------------------------------------------------------------------+
| 1. 接入与交互通道层 (Channels & Ingress)                                           |
| 客户端 (小程序/Web/APP) | 内部管理后台 | 三方 Webhook 异步回调通道                     |
+-----------------------------------------------------------------------------------+
| 2. 网关与安全护栏层 (Gateway & Safety Guardrails)                                  |
| 认证鉴权 / 速率配额 / 内容安全风控过滤 (反毒性/敏感脱敏) / 语义防重放缓存           |
+-----------------------------------------------------------------------------------+
| 3. 核心业务与控制平面 (Business Logic & Cognitive Control Plane)                  |
| 任务状态机 / 异步工作流引擎 / 提示词与上下文组装器 / 模型路由与降级网关           |
+-----------------------------------------------------------------------------------+
| 4. 外部能力与工具执行环境 (External Capabilities & Tool Execution)                |
| 多模态生图 API / 向量检索引擎 / 自动化脚本沙箱 / 第三方开放平台                     |
+-----------------------------------------------------------------------------------+
| 5. 数据与状态持久化层 (Persistence & State Stores)                                 |
| 业务关系型数据库 (PostgreSQL/MySQL) / 任务与缓存 (Redis) / 对象存储 (S3/COS/OSS)  |
+-----------------------------------------------------------------------------------+
```

## 执行步骤与检查清单

1. **界定系统边界 (System Context)**：
   - 标注所有外部参与者（Actors）与外部依赖系统（External Systems）；
   - 标明所有跨越系统边界的信息流动方向与协议基线。
2. **架构风格评估与决策**：
   - 权衡事件驱动架构（EDA）、CQRS、微服务或模块化单体；
   - 在 [architectural-style-selection-template.md](templates/architectural-style-selection-template.md) 中记录权衡论证与最终选择。
3. **绘制 AOD Mermaid 图纸与编写文字叙述**：
   - 使用 Mermaid `flowchart TD` 或 `graph TD` 绘制清晰的分层图；
   - 节点文本中严格避免未转义的特殊字符与换行；
   - 编写配套的“AOD 架构叙述”，解释每个层级的关键设计意图。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
AOD 是后续组件模型（CM）与运行模型（OM）的唯一母图。未在 AOD 中标出的关键外部依赖（如对象存储、第三方大模型 API），严禁私自在下游细化设计中引入。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “AOD 只要画几个方框就行，细节到代码里看” | AOD 的价值在于清晰呈现系统分层与数据流向，框体模糊会导致工程团队理解出现偏差。 |
| “我们是纯后端 API，不需要在 AOD 画出管理后台或三方回调” | 闭环系统必须包含逆向链路与管理控制面，缺少这些会导致架构非完整。 |
