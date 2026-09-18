---
name: component-modeling
description: "Use when breaking down systems into modular components, specifying component interfaces and dependencies, or modeling dynamic sequence flows and data lifecycles"
---

# Component Modeling (组件模型与动态时序)

## 概述

组件模型（CM, Component Model）定义了系统内部的逻辑功能单元及其相互关系。如果说 AOD 是城市的鸟瞰全景，CM 则是城市中各栋建筑的功能蓝图与内部交通连线。

在 AI / Agent 架构中，组件模型的核心焦点是**控制流与状态机解耦、提示词与模型调用隔离、以及任务生命周期事件流**。

## 适用场景 (When to Use)

- 将 AOD 中的宏观分层进一步细化为具体的模块、服务或代码包；
- 明确各组件的职责（Single Responsibility）、暴露的接口与所依赖的服务；
- 绘制系统端到端核心业务的动态时序图（Sequence Diagram）与数据流（Dataflow）；
- 避免组件间产生循环依赖与上帝对象（God Component）。

## 核心交付物与模板

- **组件模型规格说明**：[component-model-template.md](templates/component-model-template.md)

## 执行步骤与检查清单

### 步骤一：组件职责划分与依赖分析
1. 识别核心业务组件：
   - 客户端适配组件（BFF / API Gateway Adapter）；
   - 任务调度与状态机组件（Task Lifecycle Manager）；
   - AI 能力适配与防腐层组件（Model Gateway / Inpainting Adapter）；
   - 安全审查与风控组件（Guardrail & Compliance Service）；
   - 数据存储与缓存访问组件（Data Access Objects / Repositories）。
2. 绘制组件依赖拓扑图（Mermaid Graph / Flowchart）：
   - 确保依赖方向单向流动，禁止循环依赖；
   - 明确标注同步 RPC/HTTP 依赖与异步消息/事件队列依赖。

### 步骤二：组件契约与交互端口定义
为每个核心组件定义：
- **Provided Interfaces**：该组件对外部暴露的操作、方法或事件；
- **Required Interfaces**：该组件正常工作所必需的外部依赖项；
- **Invariants & Guarantees**：该组件内部维持的不变量（如幂等性保证、事务一致性）。

### 步骤三：端到端动态时序流建模
- 选取 Top 2 最关键业务场景（例如：“用户提交消除路人照片任务”、“后台管理员审批与查看调用量统计”）；
- 编写 Mermaid `sequenceDiagram`，明确标注：
  - 参与者与生命线；
  - 同步调用 vs 异步轮询/回调；
  - 异常分支与降级退避路径。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
每个组件必须具备单一明确的核心职责。严禁设计出“既负责微信鉴权、又负责调用生图模型、还负责记录账单”的超级全能组件。
在时序图中，涉及第三方不可靠网络调用处，必须明确展现超时与重试/失败分支。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “直接在控制器层调用生图 SDK，省去单独的适配层” | 第三方 SDK 存在版本变更和厂商锁定的高风险，必须通过防腐层组件（ACL）隔绝。 |
| “时序图只画成功路径，失败情况写在文档里就行” | 架构最核心的风险在于异常恢复，时序图缺少失败流意味着容灾方案未经过推演。 |
