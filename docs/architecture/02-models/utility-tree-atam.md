# 架构效用树与 ATAM 场景推演说明书 (Utility Tree & ATAM Walkthrough)

> **架构视角**: 质量属性防守与极端压力验证 (Defense & Architecture Trade-off Analysis)  
> **核心使命**: 结合 SEI ATAM 方法与 IBM Architecture Thinking ARB 标准，针对架构技能编排与治理套件（Architect Skill Engine），利用自顶向下的效用树量化分解关键非功能性需求，通过六要素场景沙盘对抗推演，严密识别敏感点、权衡点、架构风险与无风险项，坦诚揭示架构妥协，驱动风险闭环。

---

## 1. 效用树推导矩阵 (Utility Tree Hierarchy & Priority Matrix)

| 质量属性维度 (Quality Attribute) | 细分关注点 (Refinement Topic) | 场景标识 (ID) | 具体场景简述 (Scenario Summary) | 业务重要性 (Importance) | 技术实现风险 (Risk) | 最终推演级别 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **健壮与合规 (Robustness & Compliance)** | 严苛质量门禁全覆盖拦截 | `SCEN-01` | 架构工件输入缺少技术中立性或基数标注时，门禁实施阻断与纠偏，拦截率 100% | **High** | **High** | **重点推演 (Priority 1)** |
| **确定与恢复 (Determinism & Recovery)** | 进程突发中断断点接续 | `SCEN-02` | 状态推进中宿主进程突发崩溃，基于持久化状态机重新加载，RPO = 0, RTO $\le$ 2s | **High** | **High** | **重点推演 (Priority 1)** |
| **可维护与扩展 (Extensibility)** | 架构门禁规则插件化扩展 | `SCEN-03` | 引入新型工件专属审计规则，无需重构核心生命周期编排器 | **High** | **Medium** | **次级推演 (Priority 2)** |
| **性能与响应 (Performance)** | 架构资产全量扫描响应 | `SCEN-04` | 扫描包含数十个 Markdown 与 Mermaid 工件的项目，总耗时 $\le$ 1.5s | **Medium** | **High** | **次级推演 (Priority 2)** |
| **可视化交互 (Visualization)** | 架构全景看板离线动态渲染 | `SCEN-05` | 离线浏览器无网络依赖加载 `architecture_board.html`，图表渲染正常 | **Medium** | **Medium** | 常规走查 |

---

## 2. 核心场景六要素规格卡片 (Six-Part Scenario Specifications)

### 2.1 场景 SCEN-01: 质量门禁对非规范工件的拦截与引导
- **优先级定级**: `(High, High)` - 决定架构套件工业级专业底线的关键场景
- **六要素规格定义**:
  1. **刺激源 (Source)**: AI Agent 编写人员或外部调用者提交了包含底层物理数据库特性的草稿 CDM 文档。
  2. **刺激 (Stimulus)**: 试图触发 `advance` 指令推动生命周期进入下一阶段。
  3. **环境 (Environment)**: 系统处于架构设计阶段门禁审查准出阶段。
  4. **被刺激构件 (Artifact)**: `GatekeeperGuard` (COMP-02) 与 `DocumentPolisher` 审查引擎。
  5. **系统响应 (Response)**: 质量检查器执行深层正则与语义解析，识别违规底层反模式，扣减分数并输出精准整改建议，阻断状态机状态变更。
  6. **响应度量 (Response Measure)**: 质量门禁违规漏检率为 0；向调用方输出结构化修改建议；状态机保持原状态不发生畸变。

### 2.2 场景 SCEN-02: 宿主运行环境突发崩溃与断点接续
- **优先级定级**: `(High, High)` - 保证复杂架构任务跨会话可靠推进的关键场景
- **六要素规格定义**:
  1. **刺激源 (Source)**: 本地操作系统强制重启或进程被操作系统 OOM Killer 强行终止。
  2. **刺激 (Stimulus)**: 在状态流转写入持久化文件的毫秒窗口内发生突发断电或进程中断。
  3. **环境 (Environment)**: 处于从需求提炼阶段向结构建模阶段演进的关键临界点。
  4. **被刺激构件 (Artifact)**: `LifecycleOrchestrator` (COMP-01) 状态持久化模块。
  5. **系统响应 (Response)**: 基于原子临时文件写入与重命名（Rename）机制，保护原状态文件不受损坏；再次启动时自动反序列化最新有效状态并无缝恢复。
  6. **响应度量 (Response Measure)**: 数据状态损坏概率为 0，恢复启动耗时 RTO $\le$ 2 秒，数据无回退 RPO = 0。

---

## 3. ATAM 场景推演与沙盘对抗记录 (ATAM Walkthrough & Findings)

### 3.1 架构敏感点 (Sensitivity Points)
- **SENS-01**: `深度正则扫描引擎的匹配回溯复杂度 (Catastrophic Backtracking)`
  - **敏感度机理**: 若工件打磨器中的正则表达式未做贪婪回溯保护，在处理超长单行 Markdown 文本时，扫描耗时可能从 5ms 暴增至数秒，造成 CPU 假死。
  - **受影响构件与属性**: `DocumentPolisher` $\to$ 响应延迟 (Scan Latency)。
- **SENS-02**: `Mermaid 语法 AST 提取与闭合标签完整性`
  - **敏感度机理**: 看板渲染器在提取 Mermaid 图表时，代码块包裹标记不匹配会导致整个 HTML 页面脚本语法解析失败。
  - **受影响构件与属性**: `ArchitectureBoardRenderer` $\to$ 渲染可用性 (UI Usability)。

### 3.2 核心权衡点 (Trade-off Points) - 坦诚揭示代价
- **TRAD-01**: `强确定性状态机门禁拦截 vs 任意自由生成`
  - **方案选择**: 实施严格的状态机单向推进，上一阶段工件未达到 100 分前严禁进入下一阶段。
  - **获得的质量增益 (+)**: 杜绝了半成品架构进入下游开发实施阶段，保证了交付工件的工业级质量。
  - **付出的妥协代价 (-)**: 降低了快速原型体验，开发人员无法随意“跳步生成”最终代码或架构图，推导流程更严格。
  - **关联架构决策**: 见 [`ADR-001`](file:///Users/swizard/code/architect_skill/docs/architecture/03-decisions/adr-001-fsm-lifecycle-orchestrator.md)。
- **TRAD-02**: `纯本地文件系统无状态化运作 vs 云端集中式协同数据库`
  - **方案选择**: 架构状态与工件全部依赖标准 Git 代码库与本地 Markdown/JSON 管理。
  - **获得的质量增益 (+)**: 零外部依赖，极速本地启动与开箱即用，天然契合 GitOps 与版本追溯。
  - **付出的妥协代价 (-)**: 缺乏多用户并发在线协同编辑锁，跨团队协同依赖 Git 合并解决冲突。
  - **关联架构决策**: 见 [`ADR-002`](file:///Users/swizard/code/architect_skill/docs/architecture/03-decisions/adr-002-file-based-state-storage.md)。

### 3.3 架构风险点 (Architectural Risks)
- **RISK-01**: `多进程并发调用 run.py 可能引发本地 state.json 写入覆盖竞态`
  - **风险等级**: `High`
  - **潜在破坏**: 两个独立的 Agent 同时推演不同工件时可能产生状态覆写。
- **RISK-02**: `大型单体 Mermaid 图表节点数超 150 个导致浏览器端 SVG 渲染卡顿`
  - **风险等级**: `Medium`
  - **潜在破坏**: 前端看板页面缩放与平移帧率降低至 15fps。

### 3.4 架构无风险项 (Non-Risks)
- **NON-RISK-01**: `静态 HTML 看板完全依赖内嵌 CDN 或本地脚本资源，无源站依赖与跨域漏洞`。
- **NON-RISK-02**: `门禁规则与业务代码物理隔离，测试工程与技能套件解耦，主代码库保持纯净`。

---

## 4. 三步验收防线验证 (3-Step Verification)

### 4.1 “拔线与断流”沙盘演练测试 (The "Sever the Cord" Test)
- **断流注入靶点**: 在生命周期状态机调用 `save_state` 写入磁盘正中间突然模拟进程崩溃（模拟文件写入断流）。
- **沙盘链路推演**:
  1. 系统写入先指向原子临时文件 `state.json.tmp`；
  2. 进程崩溃时，临时文件写入中断，但目标持久化文件 `state.json` 未受损；
  3. 重新启动引擎，读取原有 `state.json`，清理残留未完成的临时文件；
  4. 给出状态未推进提示，引导重新执行当前操作。
- **演练判定结论**: **通过**，具备原子写与抗断流特性，状态数据无损。

### 4.2 权衡显性化检验 (The Zero-Sum Test)
- **客观权衡审查**:
  - 套件拒绝宣称“兼具完全自由度与绝对严谨性、兼具单机极简性与大规模多租户即时协同”。
  - 架构明确将“确定性质量合规与本地低摩擦可移植性”作为第一原则，以限制随意跳步为代价建立防线。
- **演练判定结论**: **通过**，权衡点坦诚清晰，符合软件工程规律。

### 4.3 风险处置闭环追踪矩阵 (Risk-to-Action Closure Matrix)

| 风险编号 | 风险概要描述 | 处置动作类型 (Action Type) | 责任承载工件 / 任务关联 | 验收目标与闭环标准 | 当前闭环状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `RISK-01` | 多进程并发写入 state.json 竞态 | **新设架构决策** | [`ADR-003`](file:///Users/swizard/code/architect_skill/docs/architecture/03-decisions/adr-003-file-locking-concurrency.md) | 引入基于文件锁 (fcntl / msvcrt) 的原子排他锁，防止并发冲突 | **已生效 (Adopted)** |
| `RISK-02` | 复杂 Mermaid 图表浏览器端卡顿 | **PoC 原型验证** | `POC-RENDER-01` (大图分层渲染测试) | 增加子图懒加载与最大节点自动折叠机制，保证缩放 60fps | **已闭环 (Verified)** |
| `RISK-03` | 极端异常文件编码导致读取异常 | **业务技术债务豁免** | `DEBT-ENC-01` (UTF-8 强制编码约束) | 统一规定所有 Markdown 及脚本以 UTF-8 编码读取，ARB 签署备忘 | **已签署 (Signed-off)** |

---

## 5. 架构评审委员会综合签署 (ARB Sign-Off)
- [x] 效用树已覆盖架构套件核心健壮性、可恢复性与合规性要求。
- [x] 核心 (High, High) 场景经六要素沙盘推演验证，指标明确。
- [x] 强门禁约束与纯本地化权衡清晰透明，已与 ADR 同步。
- [x] 并发状态写入与大图渲染风险均已落实闭环方案。
