---
name: architecture-grounding
description: "Use when capturing business drivers, clarifying non-functional requirements, formulating architecture requirements checklists (ARC), or establishing system invariant constraints"
---

# Architecture Grounding (架构锚定与需求契约)

## 概述

架构锚定是架构设计的地基。它将模糊的业务愿景与产品诉求，转化为具有明确工程边界、量化质量属性和不可突破约束的架构需求清单（ARC）。

在 AI / Agent 时代，锚定不仅包含吞吐量、并发和延迟等传统指标，更涵盖**认知有效性、Token 经济学边界、安全防御栏与确定性兜底契约**。

## 适用场景 (When to Use)

- 收到新产品、新系统或新业务线的开发诉求时；
- 需求方提出“调用大模型做某某功能”，但未定义边界、预算与安全底线时；
- 需要评估系统非功能属性（并发峰值、可用性等级、审计合规、响应 SLA）时；
- 架构评审（ARB）前建立基线度量标准时。

## 核心交付物与模板

在推进架构锚定任务时，使用本技能目录下的对应模板生成标准化文档：

1. **商业诉求与用例**：[business-driver-and-use-cases-template.md](templates/business-driver-and-use-cases-template.md)
2. **非功能性需求矩阵**：[nfr-matrix-template.md](templates/nfr-matrix-template.md)
3. **架构需求清单 (ARC)**：[arc-template.md](templates/arc-template.md)
4. **不变性约束与边界**：[constraints-template.md](templates/constraints-template.md)

## 执行步骤与检查清单

### 步骤一：商业诉求与关键用例蒸馏
- 识别系统核心 Stakeholders（最终用户、运营人员、运维保障人员、合规法务）。
- 提炼 Top 3 核心业务用例（Happy Path 与 Critical Unhappy Path）。
- 明确业务成功的量化指标（例如：日处理图片数、次日留存、单位请求成本）。

### 步骤二：AI 时代 ARC 质量属性契约化
必须针对以下四维建立量化指标：
- **认知有效性 (Cognitive Efficacy)**：
  - 任务端到端成功率目标（例如：图像消除杂物成功率 > 92%）；
  - 幻觉/无效输出容忍率上限（例如：畸变与错误生成率 < 3%）；
  - 评估数据集基准（Golden Evaluation Dataset 基线）。
- **经济学边界 (Token & Resource Economics)**：
  - 单次推理/任务处理的最大 Token/算力成本预算；
  - 高并发情况下的成本熔断阈值；
  - 缓存命中率目标（语义缓存/提示词前缀缓存）。
- **安全防御与合规 (Safety & Guardrails)**：
  - 内容合规与反毒性过滤机制；
  - 敏感数据脱敏与数据隐私（PII 防泄露）；
  - 自主工具调用的权限爆炸半径限制。
- **确定性工程 SLA (Deterministic SLAs)**：
  - 异步处理排队等待时长 SLA 与超时保护；
  - 存储高可用性与 RPO/RTO 目标。

### 步骤三：不变性约束冻结
- 法律合规约束（如必须部署在境内机房、数据保存周期）；
- 预算与运维人力约束；
- 遗留系统与三方平台协议约束（如微信开放平台接口频控与规格限制）。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
在 ARC 清单未获得需求方确认前，严禁假设外部 API 永远可用，严禁跳过非功能需求直接画组件图。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “反正调用云厂商接口，性能指标不需要我们考虑” | 第三方 API 的限流、计费和抖动直接决定你系统的生与死，必须明确定义排队与熔断基线。 |
| “成本上线后再看账单优化” | 未在 ARC 中定义单位经济学预算的系统，极容易在灰度发布时遭遇账单爆炸。 |
