# 技能库与主控规范系统级改进提案 (Skills & Evolution Proposal)

基于 `legal_contract_guardian` 案例实测中暴露的缺陷，坚持“**只修改主控、规则与模板，通过更新技能库使资产自然达标**”的原则，规划以下演进项：

## 一、 技能与模板升级规划

1. **升级 `skills/architecture-overview/`**：
   - 更新 `templates/system-context-template.md`：强制增加“上下文实体交互矩阵”标准表格、“三道安检门”与“中心黑盒实体界定”章节。
   - 更新 `SKILL.md`：在执行步骤中将交互矩阵列为必查项。
2. **升级 `skills/architecture-decisions/`**：
   - 更新 `templates/adr-template.md`：增加备选方案多维对比矩阵表格（选项、性能、成本、复杂度、逆转成本），增加“确定性锚点”与“可观测性排障代价”分析项。
3. **升级 `skills/operational-modeling/`**：
   - 更新 `templates/operational-model-template.md`：引入 Logical OM 到 Physical OM 的演进映射表以及标准节点卡片集（Node Specifications）。
4. **升级 `skills/architecture-governance/`**：
   - 更新 `templates/utility-tree-atam-template.md`：引入“六要素场景法”（刺激源、刺激、环境、构件、响应、度量）推演表。
   - 更新 `templates/technical-debt-ledger-template.md`：引入“本金(人天) + 利息(风险)”双重度量，新增“AI 认知型技术债务”识别分类。

## 二、 演进落地与回归验证
- 完成上述模板与技能规约升级；
- 重新刷新案例工作区生成物；
- 执行 `document_polisher.py` 质量复审与全量回归测试。
