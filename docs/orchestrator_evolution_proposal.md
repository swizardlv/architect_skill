# 主控引擎与规约演进提案 (Orchestrator Evolution Proposal)

## 1. 背景与反推来源
在对真实案例“照片魔法屋 (photo_magic_house)”进行首轮端到端推演与资产审计后，发现产出物在 Mermaid 语法健壮性、数据模型 DDL 完备度以及异步队列容错方案上存在体系化短板。
本提案严格贯彻“**不手工篡改案例生成物，定向反推修改主控规则与模板，通过重跑推演自然达标**”的元演进哲学。

---

## 2. 审计问题与主控根因映射表 (Finding-to-Cause Mapping)

| 审计缺陷编号 | 缺陷现象描述 | 根本病灶定位 | 主控整改落脚点与目标 |
| :--- | :--- | :--- | :--- |
| **F-01** | Mermaid 状态机连线文本包含未转义比较符（如 `重试 <= 2`）导致语法警告 | `skills/02_structural_modeling/derive_logical_domain_model.md` 缺乏对比较符引号转义的强约束 | 升级 `derive_logical_domain_model.md`，显式加入 Mermaid 语法安全规约，强制要求比较符使用双引号包裹。 |
| **F-02** | 概念数据模型仅有 ER 图，缺少生产级 DDL 与索引规划 | `skills/02_structural_modeling/derive_conceptual_data_model.md` 与模板未将物理 DDL 列为必要产出 | 升级 `derive_conceptual_data_model.md` 与 `templates/conceptual-data-model-template.md`，强制要求输出带复合索引的生产级 DDL。 |
| **F-03** | 异步任务队列 ADR 缺失消息重领（XCLAIM）与死信队列说明 | `skills/03_contracts_and_decisions/record_architecture_decision.md` 缺乏针对消息中间件决策的深度检查项 | 升级 ADR 指南，在异步解耦决策中增加消息丢失防范、死信队列（DLQ）与消费者崩溃自愈的硬性考量。 |

---

## 3. 主控元资产修改计划 (Patch Plan)
1. **修改 `skills/02_structural_modeling/derive_logical_domain_model.md`**：增加 Mermaid 状态机转义规则。
2. **修改 `skills/02_structural_modeling/derive_conceptual_data_model.md`**：在输出要求中补充生产级 DDL 与索引。
3. **修改 `skills/03_contracts_and_decisions/record_architecture_decision.md`**：增加异步架构决策的韧性契约。
