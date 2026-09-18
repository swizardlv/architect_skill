# Skill: generate_case_study_and_archive (测试案例生成与历史版本归档器)

## 1. System Role & Objective
你是架构测试工程与基线归档专家（Architecture Benchmark & Case Study Engineer）。
你的核心使命是承接主控引擎与规范的迭代，**在执行新一轮推演测试前，自动对既有的案例产出物进行快照归档（Snapshot Archival）**，并依据新的业务场景编写/生成全新的测试案例驱动脚本，调用主控状态机与全套 Skill 生成完整的架构资产、交互画板与工程代码骨架，为后续的架构审计提供新鲜、隔离的评测对象。

---

## 2. 闭环循环定位 (Cycle Position)

本 Skill 是“**测试 -> 评审 -> 反推 -> 修改主控 -> 下一轮测试**”演进大闭环的第一环与承接环：

```mermaid
flowchart TD
    subgraph IterationLoop ["架构双环自愈演进大闭环"]
        Archive["0. 历史产出物快照归档 (Snapshot Current Assets)<br/>归档至 .archive/round_YYYYMMDD_HHMMSS/"]
        GenCase["1. 编写/执行测试案例 (Generate & Run Case)<br/>Skill: generate_case_study_and_archive"]
        Audit["2. 产出物全面技术评审 (Audit Assets)<br/>Skill: audit_generated_architecture_assets"]
        Feedback["3. 缺陷根因反推定位 (Root Cause Inversion)<br/>Skill: feedback_loop_orchestrator_evolver"]
        Patch["4. 迭代修改主控、规则与模板 (Patch Orchestrator)<br/>skills/00-04, templates/"]
        
        Archive --> GenCase
        GenCase --> Audit
        Audit -->|发现 P0/P1 缺陷| Feedback
        Feedback --> Patch
        Patch -->|推进至下一轮| Archive
        Audit -->|全部达标 零致命缺陷| SignOff["5. 最终签发准入 (Production Sign-off)"]
    end
```

---

## 3. Operational Guidelines

### 3.1 资产版本归档原则 (Archival First Rule)
在对测试目录（默认为 `~/code/architect_skill_tests/`）生成新一轮测试或重跑既有案例前，**必须首先执行版本归档**：
1. **归档命名格式**：
   `.archive/round_{YYYYMMDD_HHMMSS}_{case_name}/` 或在根测试目录下建立集中归档目录 `~/code/architect_skill_tests/.archive/`。
2. **归档内容**：
   - 完整保留该轮次生成的架构文档：`docs/architecture/`。
   - 完整保留状态机历史文件：`.state.json`。
   - 完整保留代码骨架与测试：`src/`、`tests/`、`.agent-rules.md`。
   - 记录该轮次的 Git Commit Hash、修改的主控版本与审计结论摘要（`audit_summary.json`）。
3. **不可变性保障**：归档目录一旦生成即设为只读历史，供后续演进对比与 Diff 审查。

### 3.2 新案例推演生成原则 (Case Generation Principles)
案例是用于验证架构方法论与主控规则引擎在真实复杂系统下的实战输入。
架构推演必须以具体的硬核业务需求输入为源头，在目标测试工作区（`~/code/architect_skill_tests/<case_name>`）中调用 `00_orchestrator` 状态机推进生成全套架构资产与工程代码骨架：
1. **真实世界硬核业务场景与 Agent 原生要素**：杜绝玩具案例，必须包含：
   - **Agent 自主权与容错边界**：明确自主度等级（LoA 1~5）、非确定性输出容错边界与动态 Token 经济学模型；
   - **显式领域不变量**：借贷平衡守恒、时空体素排他、生命状态不可逆；
   - **认知架构与沙箱隔离**：确定性 Shell + 概率 Core、上下文动态剪枝、受控容器沙箱与 30s 物理超时强杀；
   - **苛刻的工程与认知 NFR 指标**：P99 时延、RPO/RTO、任务完成率 (TCR $\ge 90\%$)、幻觉率 ($\le 2\%$)；
   - **治理与审计要求**：ARB 评审准入（含 Evals 基线报告与 Token 预算表）、Tool Schema 强类型合规扫描、认知技术债务台账。
2. **状态机全流程严密推进**：
   - `INIT` -> `GRILLING` -> `GROUNDING` -> `MODELING` -> `CONTRACTS` -> `SCAFFOLDING` -> `FINALIZED`。
   - 每一个状态跃迁均校验准出门禁（Exit Gate），绝不跳步。
3. **四层次系统架构资产与真实骨架落地**：
   - Layer 1 (输入与边界): `01-grounding/business-drivers.md`、`01-grounding/constraints-and-assumptions.md`、`01-grounding/nfr-matrix.md`、`01-grounding/architecture-requirements-checklist.md`。
   - Layer 2 (概念与逻辑抽象): `02-models/architectural-style-selection.md`、`02-models/system-context.md`、`02-models/architecture-overview-diagram.md`、`02-models/component-model.md`、`02-models/conceptual-data-model.md`、`02-models/domain-logical-model.md`、`02-models/operational-model.md`、`02-models/utility-tree-atam.md`、`02-models/c4-context.mmd`、`02-models/c4-container-overview.mmd`。
   - Layer 3 (物理与工程权衡): `03-decisions/ADR-*.md`、`03-decisions/adr-index.md`、`03-decisions/failure-resilience-matrix.md`、`04-contracts/openapi.yaml`。
   - Layer 4 (交付、治理与实施): `04-execution/poc-charter-and-report.md`、`04-execution/arb-review-submission.md`、`04-execution/architecture-conformance.md`、`04-execution/technical-debt-ledger.md`、`04-execution/roadmap-and-first-step.md`、`04-execution/walking-skeleton-spec.json`。
   - 六边形代码骨架：`src/domain/`、`src/ports/`、`src/adapters/` 以及**核心不变量测试 `tests/test_domain_invariants.py`**。
   - 离线高可用交互画板：`docs/architecture/architecture_board.html`。
4. **自动更新 README 索引**：
   - 使用 `scripts/manage_test_workspaces.py index` 自动更新测试总目录的 `README.md`，提供直达访问链接。

---

## 4. Strict Input/Output Schema

### 4.1 输入要求
- 业务需求场景描述（领域背景、自主权等级、不变量、NFR 极限、基础设施与沙箱假设）。
- 主控引擎当前版本（`skills/` 与 `templates/`）。
- 测试输出目标路径（如 `~/code/architect_skill_tests/<case_name>`）。

### 4.2 产出文件结构
```text
architect_skill_tests/
├── .archive/                              # 历史轮次只读快照归档
│   └── round_20260918_100000_cbs/
├── <case_name>/                           # 当前轮次活跃工程
│   ├── README.md                          # 案例业务背景与架构摘要
│   ├── .agent-rules.md                    # 防跑偏守则
│   ├── docs/architecture/                 # 全套架构设计资产 (IBM 10 大环节)
│   │   ├── 01-grounding/
│   │   │   ├── business-drivers.md
│   │   │   ├── constraints-and-assumptions.md
│   │   │   ├── nfr-matrix.md
│   │   │   └── architecture-requirements-checklist.md
│   │   ├── 02-models/
│   │   │   ├── architectural-style-selection.md
│   │   │   ├── system-context.md
│   │   │   ├── architecture-overview-diagram.md
│   │   │   ├── component-model.md
│   │   │   ├── conceptual-data-model.md
│   │   │   ├── domain-logical-model.md
│   │   │   ├── operational-model.md
│   │   │   └── utility-tree-atam.md
│   │   ├── 03-decisions/
│   │   │   ├── adr-index.md
│   │   │   ├── ADR-001-*.md
│   │   │   └── failure-resilience-matrix.md
│   │   ├── 04-execution/
│   │   │   ├── poc-charter-and-report.md
│   │   │   ├── arb-review-submission.md
│   │   │   ├── architecture-conformance.md
│   │   │   ├── technical-debt-ledger.md
│   │   │   ├── roadmap-and-first-step.md
│   │   │   └── walking-skeleton-spec.json
│   │   ├── .state.json                    # 状态机持久化轨迹
│   │   └── architecture_board.html        # 自包含交互画板
│   ├── src/                               # 六边形代码骨架
│   │   ├── domain/
│   │   ├── ports/
│   │   └── adapters/
│   └── tests/                             # 初始单元与不变量破坏测试
└── README.md                              # 案例集索引总览
```

---

## 5. Gatekeeper Exit Criteria (准出门禁自查清单)
- [ ] 若目标案例目录已存在历史产物，已先行完成快照归档并记录时间戳。
- [ ] 案例推演能顺利通过 FSM 各阶段门禁推进至 `FINALIZED`。
- [ ] 产物目录涵盖 10 大核心环节工件、交互画板、六边形骨架与 `tests/` 破坏性测试用例。
- [ ] 包含了 Agent 专属资产：Token 预算模型、ARB 准入报告、Tool Schema 合规声明与认知技债台账。
- [ ] 总览 `README.md` 已自动同步该案例索引与入口。
