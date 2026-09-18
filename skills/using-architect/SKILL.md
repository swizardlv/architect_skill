---
name: using-architect
description: "Use when starting any software design or architecture task, receiving requirements, or restructuring systems before writing any implementation code"
---

# Using Architect Skills

## 核心原则

在软件开发与架构演进中，**未经架构论证与质量属性约束的代码编写是技术债务与失控的主因**。
本套架构师技能体系（Architect Skills）为 AI 编码 Agent 提供了从商业需求、概念模型、系统架构概览到运行韧性与工程治理的成套方法论。

<EXTREMELY-IMPORTANT>
只要任务涉及：
1. 搭建新系统、新功能模块或微服务；
2. 涉及模型推理、Agent 编排、多模态处理等非确定性 AI 管道；
3. 调整数据流、组件交互协议、状态存储或部署拓扑；
4. 权衡性能、成本、合规或可用性质量属性。

你必须先调用对应的架构技能，完成架构分析与设计门禁，方可进入代码实现阶段。
</EXTREMELY-IMPORTANT>

## 技能优先级与激活规则

当面对工程任务时，按照以下优先级调用技能：

1. **总控引导（Grounding）**：`architecture-grounding`
   - 蒸馏商业目标、约束条件与 NFR 指标，形成 ARC 需求清单。
2. **结构化建模（Structural Modeling）**：`architecture-overview` -> `component-modeling` -> `conceptual-data-modeling`
   - 确立系统全景（AOD）、组件边界（CM）与核心实体数据模型。
3. **契约与运行模型（Contracts & Operational Modeling）**：`operational-modeling` -> `boundary-contracts` -> `architecture-decisions`
   - 制定拓扑分布（OM）、防腐契约协议与核心 ADR 架构决策记录。
4. **实证与交付（Execution & Scaffolding）**：`architecture-execution`
   - 规划里程碑、PoC 实证试验与 Walking Skeleton 脚手架。
5. **架构治理与审计（Governance & Audit）**：`architecture-governance`
   - 执行 ARB 评审门禁、ATAM 效用树穿刺、合规扫描与技术债务登记。
6. **精细化与看板渲染（Refinement）**：`architecture-refinement`
   - 检查排版规范并渲染交互式 HTML 架构看板。

## 路径分级（Path Classification）

在行动前，明确当前任务的架构评级路径并告知用户：

- **Spike 验证型**：技术可行性探针（例如：“混元生图接口延迟与鉴权是否可行”）。
  - 产出轻量探针代码与结论备忘，标明为临时代码。
- **Bounded 局域型**：已有明确系统架构下的局部组件变更或增量功能（例如：“在后台新增一个照片状态过滤接口”）。
  - 评估局部组件契约、补充简要 ADR 或局部时序，无需重写全量 AOD。
- **Architectural 系统型**：全新业务系统、跨服务重构、引入核心 AI 能力。
  - 必须完整走过 Grounding -> Overview -> Component -> Operational -> Decision 流程，并在每个环节经用户确认后推进。

## 心智红线对照表（Red Flags）

如果你产生以下想法，说明你正在走捷径，必须立即停止并调用对应技能：

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “这个需求很简单，我直接写个 FastAPI 脚本” | 简单需求也需要明确输入边界与约束，至少完成 Grounding 确认。 |
| “我先写代码，写完再补架构图” | 事后画图是说明书，不是指导工程的架构。架构是代码的先验契约。 |
| “这是外部大模型 API，不需要做容错设计” | 外部 API 具备极高的非确定性与网络抖动，必须使用 operational-modeling 制定熔断与重试。 |
| “数据库表结构我边写边改就行” | 数据模型决定领域边界，必须先使用 conceptual-data-modeling 完成实体关系与索引设计。 |
| “技术选型很明显，不需要记录 ADR” | 显而易见的选型也需要记录上下文、假设与权衡，否则未来维护者无从追溯。 |
| “我写个简短版草稿就行，模板里的表格太啰嗦” | 模板中的结构化对比矩阵、六要素推演与安检门测试是保障架构无盲区的防火墙，严禁删减核心结构。 |

## 严禁跳步门禁（Hard Gate）

<HARD-GATE>
在任何 Architectural 路径的任务中，严禁在未产出系统概览图（AOD）和核心 ADR 之前开始编写业务逻辑代码。
生成具体架构工件时，必须严格对照各技能专属 `templates/` 中的全量结构与深度执行推演，严禁跳过方案对比矩阵、六要素场景与节点规格卡片。
每一个核心阶段的产出物，必须向用户清晰呈现并获得确认后，方可进入下一设计环节。
</HARD-GATE>
