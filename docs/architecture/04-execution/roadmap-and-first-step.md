# 架构演进路线图与第一步示踪弹穿刺 (Roadmap & Tracer Bullet PoC)

## 1. 系统演进里程碑 (Evolutionary Milestones)

| 里程碑编号 | 阶段主题 | 核心交付成果 | 验收准则与门禁 |
| :--- | :--- | :--- | :--- |
| **M0: Tracer Bullet** | 确定性状态机与门禁穿刺 | 跑通 FSM 调度器、状态持久化与硬门禁拦截 | 单元测试全通过，覆盖状态回退分支 |
| **M1: Core Skills** | 四大支柱技能深化 | 完善 AOD、CM、OM、ADR 规范与模板 | 通过 `document_polisher.py` 自动化质量门禁 |
| **M2: Visualization** | 架构看板与交互式探索 | 交付 `architecture_board.html` 与多图表联动渲染 | 实时解析 Mermaid 图表并展示状态机高亮 |
| **M3: Production Release** | 企业级流水线发布 | 形成标准化开发包与自动化测试沙箱 | 持续集成构建零告警 |

---

## 2. 第一步示踪弹穿刺规约 (Tracer Bullet Specification)

### 2.1 穿刺目标 (Hypothesis)
验证 FSM 调度引擎能否在缺少必要架构前置产物时有效阻断状态推进，并在人类输入拒绝指令时准确回退至澄清状态。

### 2.2 验证步骤与断言
1. 初始化工作区，状态置为 `INIT`。
2. 调用 `advance_lifecycle()`，校验状态单向推进至 `GRILLING`。
3. 模拟人类评审员输入 `REJECT`，验证状态精准回退至 `INIT` 且上下文无污染。
4. 模拟补充完整工件后再次推进，验证门禁放行至 `GROUNDING`。

### 2.3 验证命令
```bash
pytest -v tests/test_fsm_orchestrator.py
```