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
│   ├── architecture_diagramming_principles.md  # 架构制图准则 (吸纳 Archify 语义与排版精髓)
│   ├── generate_system_context.md              # C4 Context (L1) 建模 Prompt 与 Mermaid 规范
│   ├── derive_logical_domain_model.md          # DDD 限界上下文与生命周期状态机 Prompt
│   ├── synthesize_architecture_overview.md     # C4 Container (L2) 双环拓扑 Prompt
│   └── generate_sequence_and_dataflow.md       # 交互调用时序与分级数据流建模 Prompt
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

## 这些 Skill 到底怎么用？(实操使用方式)

详细操作与人机协同流程请参阅专属指南：👉 **[docs/skill_usage_guide.md](docs/skill_usage_guide.md)**

本项目提供三种灵活的使用形态：

### 形态 1：主控状态机联动驱动 (推荐的端到端架构推导)
由确定性 FSM 把控流程流转与门禁拦截，各阶段调用对应的 Skill 进行生成：
```bash
# 1. 运行状态机，查看当前阶段（如 GRILLING）与要求产出的目标文件
python run.py --step

# 2. 将当前阶段的 Skill（如 skills/01_grounding/grill_architecture_requirements.md）
#    作为 Prompt 喂给 AI Agent 进行交互推演，产物保存至 docs/architecture/

# 3. 产物落盘后，再次运行推进命令，状态机自动执行门禁自检与人机审核卡点（HITL）
python run.py --step
```

### 形态 2：作为 AI 辅助工具的 System Prompt / Skill 注入
- **在 Cursor / Windsurf 中**：通过 `@grill_architecture_requirements.md` 引用对应 Skill，让 AI 严格按照 Prompt 规则对你进行苏格拉底式审问或 C4 建模。
- **在 Claude Code / 自研 Agent 中**：将 `skills/**/*.md` 直接配置为 Agent 的专门 Skill 或 Subagent 角色指令。

### 形态 3：单点独立使用 (离线设计与评审)
无需启动整个生命周期，直接按需调用：
- 想写一份标准的架构决策？直接参考 `skills/03_contracts_and_decisions/record_architecture_decision.md` 并套用 `templates/adr-template.md`。
- 想厘清系统与外部三方的依赖与防腐层？直接使用 `skills/02_structural_modeling/generate_system_context.md` 绘制 Mermaid C4 图。

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

### 3. 编译输出交互式架构全景画板 (Archify 风格)
```bash
# 将 02-models/ 下的架构图表编译为自包含单文件 HTML 画板
python run.py --render-board

# 生成产物路径：docs/architecture/architecture_board.html
# 支持浏览器直接打开、双主题切换、平移缩放 (Pan & Zoom) 与高清 SVG 导出
```
