# 架构工程化落地手册与规范指南

## 1. 体系定位与核心哲学

本工程旨在将高级架构思维（Architecture Thinking）与“确定性工程外壳 + 概率性推理内核（Deterministic Shell + Stochastic Core）”的方法论沉淀为可直接在生产环境落地的自动化代码、Prompt 规范与模板工程。

面对传统软件与现代智能体（Agent）开发中的两极分化——即“过度依赖概率推理导致逻辑失控与代码熵增”，或者“过度僵化导致无法利用大模型语义泛化能力”——本体系提供了一套物理围栏：
1. **宏观控制由有限状态机（FSM）掌控**：状态单向演进，阶段资产具备单向基线锁定与准出门禁检查（Gatekeeper Validation），关键决策节点阻塞等待人类确认（HITL）。
2. **微观推理交由智能体在沙箱内完成**：在明确的上下文视图、AST 符号索引和强类型契约内生成局部补丁与概念模型，严禁越界读写。
3. **向下游 Vibe Coding 施加三大红线**：通过 `.agent-rules.md` 锁定契约只读、单向依赖倒置与测试自检闭环，确保 AI 编码助手不偏离架构轨道。

---

## 2. 工程目录体系与资产拓扑

```text
skills/
├── 00_orchestrator/
│   ├── orchestrate_architecture_lifecycle.py   # 主控状态机驱动引擎 (FSM 调度实现)
│   ├── fsm_config.json                         # 状态转移规则、门禁与路径配置
│   └── README.md                               # 编排引擎运行说明与 CLI 命令
├── 01_grounding/
│   ├── grill_architecture_requirements.md      # 苏格拉底式审问 Prompt 与准出门禁
│   ├── distill_nfr_matrix.md                   # NFR 度量矩阵提取 Prompt 与模板
│   └── catalog_invariants_and_constraints.md   # 不变量与硬约束编目 Prompt 与模板
├── 02_structural_modeling/
│   ├── generate_system_context.md              # C4 Context (L1) 建模 Prompt 与 Mermaid 规范
│   ├── derive_logical_domain_model.md          # DDD 限界上下文与状态机 Prompt
│   └── synthesize_architecture_overview.md     # C4 Container (L2) 拓扑 Prompt
├── 03_contracts_and_decisions/
│   ├── record_architecture_decision.md         # ADR 决策生成 Prompt (MADR 规范)
│   ├── scaffold_boundary_contracts.md          # OpenAPI / JSON Schema 提取与验证 Prompt
│   └── generate_failure_resilience_matrix.md   # FMEA 容灾降级矩阵 Prompt
├── 04_execution_and_scaffolding/
│   ├── bootstrap_walking_skeleton.md           # 工程物理骨架生成 Prompt
│   └── sequence_delivery_milestones.md         # 敏捷里程碑与 First Step PoC Prompt
templates/                                      # 产出文档的标准 Markdown / YAML 模板
│   ├── nfr-matrix-template.md
│   ├── constraints-template.md
│   ├── adr-template.md
│   ├── resilience-matrix-template.md
│   └── agent-rules-template.md                 # 供 Vibe Coding 防跑偏的 .agent-rules 核心模板
tests/
│   └── test_fsm_orchestrator.py                # 针对主控状态机推进、卡点与拦截的单元测试
└── run.py                                      # 启动交互式架构设计会话的入口脚本
```

---

## 3. 状态机推进与门禁规则说明

有限状态机严格按照以下顺序推进：
`INIT` -> `GRILLING` -> `GROUNDING` -> `MODELING` -> `CONTRACTS` -> `SCAFFOLDING` -> `FINALIZED`

### 3.1 门禁拦截策略
- **不可跳步**：若当前阶段前置产物（如 `grounding-spec.json`）缺失或格式损坏（如非法 JSON），状态机抛出 `GatekeeperError` 并中断跃迁。
- **人机审查卡点 (HITL)**：
  - 在 `GRILLING` 准出时：要求确认业务驱动力、NFR 目标与核心不变量。
  - 在 `CONTRACTS` 准出时：要求签署架构决策（ADR）、OpenAPI 强类型契约与 FMEA 容灾降级矩阵。
- **打回与自愈**：若人类审查判定不合格并打回，状态机自动记录打回原因并回退到上一工作状态。

---

## 4. 运行与验证指令

```bash
# 执行单元测试套件
pytest -v

# 查看状态机状态
python run.py --status

# 交互式单步流转
python run.py --step

# 生成全链路演示资产并自动批准推进
python run.py --init-sample-assets
python run.py --auto-approve
```

---

## 5. CI 持续集成与自动化流水线 (GitHub Actions)

项目内置 `.github/workflows/ci.yml` 自动化工作流，在提交或拉取请求时自动触发：
1. **多版本矩阵验证**：覆盖 Python 3.11 与 3.12 运行时。
2. **静态语法检查**：执行 `npm run lint` 验证 Python 核心逻辑与测试模块编译合法性。
3. **单元测试回归**：执行 `npm run test`（`pytest -v`），验证门禁拦截、状态持久化与全生命周期流转。
4. **端到端冒烟测试**：运行 `run.py` 驱动状态机自检，验证演进闭环与退出状态。

