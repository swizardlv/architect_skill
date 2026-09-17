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
案例是用于验证架构能力与方法论的真实输入，**严禁在 `architect_skill` 核心代码库中硬编码业务案例脚本**。
架构推演必须以具体的业务需求输入（PRD / 架构盘问记录）为源头，直接在目标测试工作区（`~/code/architect_skill_tests/<case_name>`）中调用 `00_orchestrator` 状态机推进生成全套架构资产：
1. **真实世界硬核业务场景**：杜绝 Hello World 级别的玩具案例，必须包含：
   - 显式的业务不变量（如：强一致守恒、时空排他、生命体征不可逆）。
   - 苛刻的 NFR 指标（明确数字：TPS、P99 毫秒、RPO/RTO）。
   - 复杂的异常容灾场景（单点故障、网络分区、超时挂死）。
2. **状态机全流程严密推进**：
   - `INIT` -> `GRILLING` -> `GROUNDING` -> `MODELING` -> `CONTRACTS` -> `SCAFFOLDING` -> `FINALIZED`。
   - 每一个状态跃迁均校验准出门禁（Exit Gate），不跳步。
3. **四层次系统架构资产与真实骨架落地**：
   - Layer 1 (输入与边界): `00-grounding/business-driver-and-use-cases.md`, `00-grounding/grounding-spec.json`, `01-grounding/nfr-matrix.md`, `01-grounding/constraints-and-assumptions.md`。
   - Layer 2 (概念与逻辑抽象): `02-models/architecture-overview.md`, `02-models/domain-logical-model.md`, `c4-context.mmd`, `c4-container-overview.mmd`。
   - Layer 3 (物理与工程权衡): `03-decisions/deployment-and-observability.md`, `03-decisions/adr-index.md`, `03-decisions/failure-resilience-matrix.md`, `04-contracts/openapi.yaml`, `04-contracts/interface-contracts-overview.md`。
   - Layer 4 (组织与交付实施): `.agent-rules.md`, `04-execution/organization-and-plan.md`, `04-execution/roadmap-and-first-step.md`, `04-execution/walking-skeleton-spec.json`。
   - 六边形代码骨架：`src/domain/`、`src/ports/`、`src/adapters/` 以及**核心不变量测试 `tests/test_domain_invariants.py`**。
   - 离线高可用交互画板：`docs/architecture/architecture_board.html`。

4. **自动更新 README 索引**：
   - 使用 `scripts/manage_test_workspaces.py index` 自动更新测试总目录的 `README.md`，提供直达访问链接。


---

## 4. Strict Input/Output Schema

### 4.1 输入要求
- 业务需求场景描述（领域背景、不变量、NFR 极限、基础设施假设）。
- 主控引擎当前版本（`skills/00_orchestrator/`）。
- 测试输出目标路径（如 `~/code/architect_skill_tests/`）。

### 4.2 产出文件结构
```text
architect_skill_tests/
├── .archive/                              # 历史轮次只读归档
│   └── round_20260917_100000_cbs/
├── <case_name>/                           # 当前轮次活跃工程
│   ├── README.md                          # 案例业务说明
│   ├── .agent-rules.md                    # 防跑偏守则
│   ├── docs/architecture/                 # 全套架构设计资产
│   │   ├── 00-grounding/
│   │   ├── 01-grounding/
│   │   ├── 02-models/
│   │   ├── 03-decisions/
│   │   ├── 04-contracts/
│   │   ├── 04-execution/
│   │   ├── .state.json
│   │   └── architecture_board.html        # 架构画板
│   ├── src/                               # 六边形代码骨架
│   └── tests/                             # 初始单元与不变量破坏测试
└── README.md                              # 案例集索引总览
```

---

## 5. Gatekeeper Exit Criteria (准出门禁自查清单)
- [ ] 若目标案例目录已存在历史产物，已完整完成快照归档并记录时间戳。
- [ ] 新案例已在 `scripts/run_case_study.py` 中完成注册并可通过 CLI 驱动。
- [ ] 案例推演能顺利通过 FSM 各阶段门禁推进至 `FINALIZED`。
- [ ] 产物目录完整包含架构文档、交互画板、六边形骨架与 `tests/` 破坏性测试用例。
- [ ] 总览 `README.md` 已自动同步该案例索引与入口。
