---
name: architecture-governance
description: "Use when conducting Architecture Review Board (ARB) hearings, performing ATAM quality attribute walkthroughs, checking architectural drift conformance, or auditing technical debt ledgers"
---

# Architecture Governance (架构治理、评审与技术债务)

## 概述

架构治理是保证系统在长期生命周期中不失控、不退化、不偏离既定契约的防御系统。

在 AI / Agent 时代，大模型迭代迅速、提示词与业务逻辑容易交织漂移，因此架构治理必须建立**严密的 ARB 评审门禁、基于 ATAM 的效用树压力穿刺、自动化的架构合规扫描与技术债务动态台账**。

## 适用场景 (When to Use)

- 系统设计完成、正式启动编码实施前的架构评审（ARB Gate）；
- 评估极端业务场景下的架构韧性与权衡点（ATAM 效用树穿刺）；
- 检测代码实现是否发生“架构漂移”（如上层直接跨层直连数据库、或绕过安全网关直连外部模型）；
- 系统上线前后登记技术债务、评估折旧利息与归还时间表。

## 核心交付物与模板

1. **ARB 架构评审申报与决议表**：[arb-review-submission-template.md](templates/arb-review-submission-template.md)
2. **ATAM 效用树与情景穿刺报告**：[utility-tree-atam-template.md](templates/utility-tree-atam-template.md)
3. **架构合规性扫描规约**：[architecture-conformance-spec-template.md](templates/architecture-conformance-spec-template.md)
4. **技术债务台账与还款计划**：[technical-debt-ledger-template.md](templates/technical-debt-ledger-template.md)

## 执行步骤与检查清单

### 步骤一：ARB（架构评审委员会）门禁审查
审查委员会围绕四大核心支柱进行裁决：
- **一致性与规范性**：AOD、CM、OM 与数据模型是否相互印证、无断裂；
- **非确定性控制**：对外部 AI 接口的超时、重试、并发限流与熔断策略是否闭环；
- **安全与合规边界**：敏感数据传输、多租户鉴权、涉黄涉政过滤与审计日志是否符合法律红线；
- **裁决结论**：明确给出 `通过 (Approved)`、`带条件通过 (Approved with Conditions)` 或 `否决重修 (Rejected)`。

### 步骤二：ATAM 效用树穿刺与敏感点分析
- 构建三级效用树（质量属性 -> 细分维度 -> 具体压力场景）；
- 对关键场景（例如：“突发流量翻 10 倍且外部模型响应时间从 3s 骤增到 15s”）进行推演；
- 识别**敏感点 (Sensitivity Points)**与**权衡点 (Trade-off Points)**，发现架构隐患。

### 步骤三：架构合规检查 (Conformance Check)
- 验证物理代码实现是否遵循分层防腐约束；
- 检查是否存在绕过网关直接硬编码外部 API Key 的行为；
- 检查是否存在未捕获的外部网络异常分支。

### 步骤四：技术债务台账化管理
- 任何为了赶工期或妥协而采取的权宜之计（如临时单机内存缓存、未做分库分表），必须录入 [technical-debt-ledger-template.md](templates/technical-debt-ledger-template.md)；
- 标明债务等级、产生利息（对运维/稳定性的持续消耗）与拟归还版本号。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
凡被 ARB 裁定为“否决重修”的架构方案，严禁进入生产代码交付阶段。
严禁存在“隐形债务”——所有被识别的妥协点必须全部登账，责任到人。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “ARB 评审只是走个形式，直接开干就行” | ARB 门禁能拦截 80% 以上由于模型外部依赖考虑不周带来的灾难性架构返工。 |
| “技术债务以后想起来再改” | 没有台账和偿还排期的技术债务，最终都会演变成压垮系统的致命故障。 |
