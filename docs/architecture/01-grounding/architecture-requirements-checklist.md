# 架构需求核对与质量保障清单 (Architecture Requirements Checklist, ARC)

> **架构视角**: 质量工程与非功能契约 (Quality Engineering & Contractual Guardrails)  
> **核心使命**: 将架构编排技能套件中的模糊期望（如“快速响应”、“可靠状态推进”、“看板直观”），转化为不可篡改、可度量、可验证且直接驱动 AOD、CM、OM、ADR 的工程契约铁笼。  
> **制定铁律**: **任何无法被自动化测试或量化验收的描述，都是无效条款。**

---

## 1. URPS+ 架构需求全景闭环矩阵 (URPS+ Master Matrix)

| 需求编号 | 质量属性维度 (URPS+) | 详细需求场景与指标描述 (Scenario & Target Metrics) | 架构推导映射 (Mapping to CM / OM / ADR) | 自动化验证与验收方式 (Verification Method) | 闭环状态 (Status) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ARC-PERF-01** | **Performance & Scalability**<br>(性能与弹性) | **状态机单步跃迁**: 状态转移耗时 ≤ 50ms<br>**看板生成时延**: HTML 看板渲染生成耗时 ≤ 500ms<br>**文档审计速率**: 50 个 Markdown 文件质量打磨审计耗时 ≤ 2 秒 | • **CM**: `FSMOrchestrator`, `BoardRenderer`<br>• **OM**: 本地轻量进程运行，内存常驻占用 < 120MB<br>• **ADR**: [ADR-001](../03-decisions/ADR-001-fsm-shell.md) (确定性 FSM 调度器) | 单元测试基准耗时断言（`test_fsm_orchestrator.py` 执行时耗 < 0.1s） | 已验证 (Verified) |
| **ARC-AVAIL-01** | **Availability & Resiliency**<br>(可用性与容灾) | **断点无损恢复**: 任意会话崩溃或强制终止，状态与上下文恢复 **RTO** < 500ms<br>**数据零丢失**: 状态机迁移日志与产物映射严格 **RPO = 0**<br>**合法跳转防护**: 非法跳转与产物缺失拦截率 100% | • **CM**: `GatekeeperGuard`, `StateManager`<br>• **OM**: 基于本地文件系统 WAL 临时原子重命名持久化<br>• **ADR**: [ADR-001](../03-decisions/ADR-001-fsm-shell.md) (状态快照持久化) | 单元测试测试用例断网与崩溃模拟（`test_state_persistence_and_resume`） | 已验证 (Verified) |
| **ARC-SEC-01** | **Security & Compliance**<br>(安全与合规) | **隔离保护**: 外部命令执行必须在沙箱或受限子进程运行，超时强制杀进程 (Hard Timeout ≤ 30s)<br>**权限受限**: 严禁越权修改非架构文档目录<br>**代码合规**: 核心代码库杜绝混入具体业务代码 | • **CM**: `WorkspaceManager` 隔离沙箱<br>• **OM**: 工作区物理路径隔离，测试案例位于测试工作区<br>• **ADR**: 纯净架构资产与隔离规范 | CI 静态代码扫描与测试工作区越权检测 | 已验证 (Verified) |
| **ARC-OPS-01** | **Manageability & Observability**<br>(运维与可观测性) | **架构状态透明度**: 交互式看板 100% 实时同步 FSM 状态与 Mermaid 图表<br>**质量度量透明度**: `document_polisher.py` 对各工件输出量化评分 (0-100分)<br>**日志诊断**: 详细记录每一次门禁拦截与人类打回原因 | • **CM**: `DocumentPolisher`, `BoardRenderer`<br>• **OM**: 本地日志输出与静态 HTML 看板文件<br>• **ADR**: 架构质量自动化门禁机制 | 运行 `document_polisher.py` 自动化审查全库文档 | 已批准 (Approved) |
| **ARC-INT-01** | **Integrability & Portability**<br>(集成性与可移植性) | **运行环境兼容**: 支持 macOS / Linux，兼容 Python 3.10+ 与 Node.js 18+<br>**标准图元规范**: 100% 遵从 Mermaid 官方语法与通用 Markdown 渲染<br>**工具链联动**: 支持与 IDE 命令行及 CI/CD 管道无缝集成 | • **CM**: `DiagramRenderer` 跨平台图元适配层<br>• **OM**: 标准 npm / pytest CLI 驱动支持<br>• **ADR**: 统一标准开发包与 CLI 交互规约 | `npm run compile && npm run lint && npm test` 自动化集成构建 | 已验证 (Verified) |

---

## 2. SEI 质量属性场景六要素深化卡片 (Quality Attribute Scenarios)

### 场景卡片 1: 缺少架构产物时的非法跳转拦截 (对应 ARC-AVAIL-01)
- **刺激源 (Source)**: 开发者或大语言模型在未产出 AOD 架构概览图时调用推进指令。
- **刺激 (Stimulus)**: 发送 `ADVANCE` 事件试图将状态从 `GRILLING` 强行跳跃到 `GROUNDING`。
- **环境 (Environment)**: 会话正在进行中，工作区目录缺少必要产物文件。
- **被刺激对象 (Artifact)**: 门禁守护者模块 (`Gatekeeper`) 与状态调度引擎 (`FSMOrchestrator`)。
- **系统响应 (Response)**:
  1. 门禁检查发现前置产物检查清单未满足；
  2. 立即阻止状态迁移，保持当前状态不变；
  3. 返回明确的缺失文件清单与指引。
- **响应度量 (Measure)**: **非法状态跳转拦截率 100%**，状态文件零污染，耗时 ≤ 10ms。

### 场景卡片 2: 会话异常崩溃后的断点续接 (对应 ARC-AVAIL-01)
- **刺激源 (Source)**: 宿主系统突然异常断电或终端进程被强制 SIGKILL 终止。
- **刺激 (Stimulus)**: 处于 `STRUCTURAL_MODELING` 状态时的进程突然被杀。
- **环境 (Environment)**: 复杂多步架构推导进行中，已生成部分中间模型。
- **被刺激对象 (Artifact)**: 状态持久化管理器 (`StateManager`)。
- **系统响应 (Response)**:
  1. 新会话启动并调用调度引擎；
  2. 自动检测并加载本地落盘的状态快照；
  3. 校验已落地工件并恢复至中断前的状态点。
- **响应度量 (Measure)**: **恢复用时 RTO < 500ms**，已确认状态与上下文数据 **RPO = 0 (零丢失)**。

---

## 3. 五位一体全要素联动闭环 (Five Pillars Alignment)

```
                    +---------------------------------------------+
                    |        ARC 架构需求核对清单 (量化标尺)        |
                    | (FSM跃迁≤50ms / RTO<500ms / RPO=0 / 100%拦截) |
                    +----------------------+----------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v 驱动结构设计                                 v 裁决选型与代价
+--------------------------------------+      +--------------------------------------+
| 1. AOD: 架构技能套件概览与边界        |      | 4. AD/ADR: 架构决策法典              |
|    解耦编排核心、门禁、渲染与打磨模块  |      |    • 为什么在 ADR-001 否决网状自由模型?|
| 2. CM: 逻辑组件与接口契约            | <--> |      因为无法达成 ARC-AVAIL 100% 拦截!|
|    Provided/Required 契约与状态所有权|      |    • 为什么状态机采用本地 WAL 持久化? |
| 3. OM: 运行环境与目录布局            |      |      因为满足 ARC-AVAIL 的零丢失恢复! |
|    轻量单进程、标准 npm/pytest CLI   |      |    • 针对状态复杂度在 CM 设立看板映射 |
+--------------------------------------+      +--------------------------------------+
                    \                                             /
                     \                                           /
                      v                                         v
                    +---------------------------------------------+
                    |       5. 系统交付验收与自动化测试验证 (CI)    |
                    |      pytest 11 项单测 + npm 编译全量闭环通过   |
                    +---------------------------------------------+
```

---

## 4. 架构委员会审计签署 (ARB Sign-off)
- **主导架构师**: APPROVED (2026-09-18)
- **质量工程与测试代表**: APPROVED (2026-09-18)
- **综合评审结论**: 准予进入下一阶段 (APPROVED TO PROCEED)
