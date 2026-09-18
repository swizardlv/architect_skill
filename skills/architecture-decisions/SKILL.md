---
name: architecture-decisions
description: "Use when making irreversible architectural trade-offs, formulating Architecture Decision Records (ADR), evaluating foundational technology stacks, or resolving design controversies"
---

# Architecture Decisions (架构决策记录 ADR)

## 概述

架构决策记录（ADR, Architecture Decision Record）是记录软件系统演进过程中关键架构选择的历史档案。它不仅记录“选了什么”，更详细记录“面对何种业务上下文、在哪些备选方案中权衡、做出了什么假设、接受了哪些妥协后果”。

在 AI / Agent 时代，决策博弈从传统的语言/数据库选型，拓展为**模型托管权、非确定性控制、单位经济学生存边界与自主爆炸半径控制**。

## 适用场景 (When to Use)

- 选定或更换核心技术栈、数据库或中间件时；
- 决定大模型接入模式（云厂商公有云 API vs 自建开源模型微调）；
- 决定长耗时多模态推理的调度机制（消息队列异步驱动 vs WebSocket 长连接）；
- 涉及数据合规、用户隐私保护与内容风控拦截策略时。

## 核心交付物与模板

- **标准架构决策记录模板**：[adr-template.md](templates/adr-template.md)

## AI 时代六大核心 ADR 权衡焦点

在设计 AI/Agent 架构时，必须重点对以下六类决策做出论证并沉淀为 ADR：

1. **认知推理供给模式**：公有云商用 API（弹性强、前期成本低） vs 私有化/开源自建（数据独占、延迟可控、固定资产开销大）；
2. **交互范式与工作流调度**：同步阻塞请求（仅限 < 1s 极轻量调用） vs 异步轮询/Webhook 回调（应对秒级长耗时生成任务）；
3. **模型分工架构**：单一超强泛化大模型（提示词工程简单、费用极高） vs 专家模型梯队混合路由（SLM 分类/初筛 + LLM 复杂推理，降低 80% Token 消耗）；
4. **状态持久化与上下文管理**：全量持久化状态机（可重放、支持任意节点断点续跑） vs 内存短暂上下文（吞吐高、但无法审计与灾备）；
5. **安全护栏拦截层级**：前置规则引擎与轻量模型拦截（零 Token 成本、速度极快） vs 后置大模型全量语义审查（理解深但增加调用延迟与成本）；
6. **多租户与资源配额控制**：基于用户等级的硬配额限流 vs 动态优先级抢占式队列。

## 执行步骤与检查清单

1. **描述决策背景 (Context)**：
   - 清楚陈述驱动该决策的技术现实、业务诉求与约束条件。
2. **列举备选方案与权衡 (Considered Options)**：
   - 至少列出 2-3 个可行备选方案；
   - 逐一对比各方案的优缺点（Pros and Cons）；
   - 提供定性或定量分析（如吞吐量、成本、开发周期）。
3. **明确决策结果 (Decision Outcome)**：
   - 明确选用哪一个方案；
   - 明确阐述选择该方案的核心理由（Justification）。
4. **记录积极与消极后果 (Consequences)**：
   - 必须坦诚记录引入该方案带来的负面代价（Negative consequences / Trade-offs）；
   - 提出针对负面代价的缓解策略（Mitigation）。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
任何后果栏写着“无负面影响”的 ADR 均判定为无效文档。任何架构选择都存在取舍，掩盖妥协后果意味着技术风险未被充分评估。
系统核心技术选型必须具备正式的 ADR 编号与状态标记（Proposed, Accepted, Rejected, Deprecated）。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “用混元生图 API 是默认的，不需要写 ADR” | 依赖特定商业 API 是极高的外部依赖风险，必须在 ADR 中分析计费阶梯、频控上限与厂商替代备选方案。 |
| “ADR 太啰嗦，写在代码注释里就行” | 代码注释随代码流转，无法供全组织、ARB 审查以及跨部门架构师协同评审。 |
