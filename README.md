# 架构设计方法论与执行 Skill 工程体系 (Architect Skill)

本项目基于“**确定性工程外壳 + 概率性推理内核 (Deterministic Shell + Stochastic Core)**”的方法论，将架构设计全生命周期的 12 个核心 Skill 原型沉淀为生产级可执行代码、Prompt 规范与模板工程。

---

## 目录索引与工程结构

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
├── docs/                                       # 架构文档与工程指南
│   ├── architecture_engineering_handbook.md    # 架构落地手册
│   └── architecture/                           # 架构资产工作空间及 .state.json 状态记录
├── .agent-rules.md                             # 根目录防跑偏守则（契约只读/依赖倒置/自检闭环）
└── run.py                                      # 启动交互式架构设计会话的入口脚本
```

---

## 核心机制与三大防跑偏红线

下游使用 Cursor、Windsurf、Claude Code 等 AI 编程助手进行 Vibe Coding 时，根目录的 `.agent-rules.md` 强制生效：
1. **只读契约目录**：`docs/architecture/`、`04-contracts/` 与抽象端口定义只读，严禁在编码阶段反向篡改契约。
2. **单向依赖倒置**：`domain/` 严禁引入具体框架、数据库 SDK 或网络适配器。
3. **测试沙箱自检闭环**：代码提交前必须执行静态检查与测试，严禁修改既有测试以迎合错误实现。

---

## 快速开始

### 1. 运行质量检查与测试套件
```bash
npm run lint
npm run test
# 或者直接使用 Python
pytest -v
```

### 2. 状态机调度与交互推进
```bash
# 查看当前架构生命周期状态
python run.py --status

# 交互式单步推进（遇到 HITL 门禁提示审批确认）
python run.py --step

# 生成演示架构资产并自动批准推进
python run.py --init-sample-assets
python run.py --auto-approve

# 重置生命周期状态
python run.py --reset
```
