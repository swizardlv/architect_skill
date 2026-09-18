# Architect Skill (AI 架构师方法论技能体系)

Architect Skill 是一套专为 AI 编码 Agent 打造的软件架构工程方法论与技能体系。它构建在一组高度内聚、微内核化的架构技能以及自举式引导机制之上，确保你的 AI Agent 在写下第一行代码前，真正像一名资深主任架构师一样思考与推演。

---

## 目录 (Table of Contents)

- [运作原理 (How It Works)](#运作原理-how-it-works)
- [基础工作流 (The Basic Workflow)](#基础工作流-the-basic-workflow)
- [技能库清单 (What's Inside)](#技能库清单-whats-inside)
- [设计哲学 (Philosophy)](#设计哲学-philosophy)
- [安装与配置 (Installation)](#安装与配置-installation)
  - [Antigravity](#antigravity)
  - [Claude Code](#claude-code)
  - [Cursor](#cursor)
  - [Codex CLI / App](#codex-cli--app)
  - [Gemini CLI](#gemini-cli)
- [工程质量与自动化检查 (Testing & Verification)](#工程质量与自动化检查-testing--verification)
- [贡献指南 (Contributing)](#贡献指南-contributing)
- [许可证 (License)](#许可证-license)

---

## 运作原理 (How It Works)

它的效力，从你启动 AI 编码 Agent 的那一刻便已生效。

每当 Agent 检测到你准备构建一个新系统、新增业务模块或调用大模型 API 时，它**绝不会**毛手毛脚地立刻开始创建文件和写业务代码。相反，它会退后一步，通过苏格拉底式提问追问你真正想达成的业务目的、核心用例与吞吐边界。

当它从对话中提炼出需求后，不会一次性抛出几千字的冗长报告，而是分章节呈现设计方案，在每个关键决策点停下征询你的确认。

在设计方案获得你的首肯后，Agent 会运用严密的架构思维推演全局：从分层架构概览图（AOD）、组件拓扑与时序（CM）、物理部署与故障韧性（OM），到数据模型（CDM）与生产级 DDL。更重要的是，在面对大模型等非确定性外部依赖时，它会主动建立熔断降级、异步排队、敏感词安全过滤与 Token 经济学防线。

一旦你发出开始指令，它会搭建端到端打通的最小骨架系统（Walking Skeleton），并在需要时通过靶向 PoC 实验消除外部 API 的未知风险，随后才进入稳定的编码交付。

因为所有技能均配置了自动触发与上下文注入钩子，你无需记忆繁琐的指令——你的 Agent 自然拥有了资深架构师的思考深度与工程纪律。

---

## 基础工作流 (The Basic Workflow)

1. **using-architect** - 会话启动即生效。建立架构优先原则，设置心智红线表（Red Flags）拦截走捷径思维，将任务划分为 Spike、Bounded 或 Architectural 三级路径。
2. **architecture-grounding** - 在动手前激活。蒸馏商业目标与关键用例，制定涵盖认知有效性、Token 预算与确定性 SLA 的 ARC 架构需求清单。
3. **architecture-overview** - 在需求锚定后激活。绘制系统上下文图（System Context）与 5 层架构概览图（AOD），确定整体架构风格与三方系统物理边界。
4. **component-modeling** - 在概览确定后激活。分解组件职责、定义交互端口，绘制核心业务的动态调用时序图与数据流向。
5. **operational-modeling** - 在组件确立后激活。将逻辑组件映射至计算节点，规划网络分区、全链路可观测性以及应对三方 API 故障的容错韧性矩阵。
6. **conceptual-data-modeling** - 在数据边界明确后激活。设计 ER 实体模型，规划关系库、缓存与对象存储的多模拓扑，输出包含复合索引的生产级 DDL。
7. **boundary-contracts** - 在接口开发前激活。规范前后端 API 协议、异步任务轮询契约、事件队列 Schema 以及防腐层（ACL）适配标准。
8. **architecture-decisions** - 贯穿设计全过程。针对不可逆的技术选型与争议点输出标准 MADR 架构决策记录，坦诚记录负面代价与权衡理由。
9. **architecture-execution** - 在实现前夕激活。规划垂直切片里程碑，通过极简 Walking Skeleton 骨架与靶向 PoC 实验验证关键假设。
10. **architecture-governance** - 在方案定稿后激活。通过 ARB 评审门禁审查、ATAM 效用树穿刺、架构漂移扫描与技术债务登账。
11. **architecture-refinement** - 交付阶段激活。运行排版工具自查格式，渲染高可视化、支持实时交互缩放的单页 HTML 架构看板。

**Agent 在行动前必须检索对应技能。这是强制性工作流，而非可选建议。**

---

## 技能库清单 (What's Inside)

### 需求与基线 (Grounding)
- **architecture-grounding** - 商业愿景提炼、NFR 指标矩阵、ARC 架构需求清单与系统不变性约束编目。

### 结构与建模 (Structural Modeling)
- **architecture-overview** - 系统上下文边界图、5 层工业级 AOD 概览图与架构风格选型决策。
- **component-modeling** - CM 模块职责划分、依赖拓扑单向约束、交互端口与端到端动态时序流。
- **conceptual-data-modeling** - 核心业务实体 ER 关系图、生产级 DDL 建表脚本与多模持久化划分。

### 契约与运行 (Contracts & Operations)
- **operational-modeling** - 物理运行节点拓扑、网络安全隔离域、故障韧性矩阵与全链路可观测性。
- **boundary-contracts** - 同步 RESTful API、异步轮询规范、事件队列载荷与防腐层适配契约。
- **architecture-decisions** - MADR 标准架构决策记录，涵盖 AI 时代 6 大核心决策博弈。

### 实证与治理 (Execution & Governance)
- **architecture-execution** - 垂直切片交付编排、端到端 Walking Skeleton 脚手架与靶向 PoC 实验章程。
- **architecture-governance** - ARB 评审委员会门禁裁决、ATAM 效用树情景穿刺、架构合规扫描与技术债务台账。

### 元技能与工具 (Meta & Tooling)
- **using-architect** - 技能调度总则、心智红线拦截表与分级路径指南。
- **architecture-refinement** - 文档排版自动化检查工具与单页交互式 HTML 架构看板生成器。

---

## 设计哲学 (Philosophy)

- **先契约后实现 (Contracts Over Code)**：架构是代码的先验契约，代码是契约的运行时具象。
- **正视非确定性 (Design For Stochastic Realities)**：在概率性大模型之上构建系统，必须依靠确定性的工程外壳提供熔断、重试与兜底。
- **透明妥协与可追溯性 (Trade-Offs Over Pretended Perfection)**：没有零代价的架构选型。坦诚记录负面后果，将其纳入技术债务台账。
- **实证重于声称 (Evidence Over Claims)**：未经 PoC 探针验证的技术假设只是猜想，上线前必须以数据量化评判。
- **极简高内聚 (Simplicity & Cohesion)**：每个技能微内核自治，附属模板和脚本自成体系，坚决消除跨层冗余。

---

## 安装与配置 (Installation)

不同开发环境的安装方式如下：

### Antigravity
直接作为插件从仓库或本地目录加载：
```bash
agy plugin install https://github.com/swizard/architect_skill
```
Antigravity 会自动执行 `hooks/session-start` 钩子，自首条消息起即刻注入 `using-architect` 规则上下文。

### Claude Code
通过本地插件机制添加：
```bash
claude plugin add /path/to/architect_skill
```

### Cursor
在 Cursor 对话框中引用技能目录，或将技能挂载至 `~/.agents/skills/` 共享目录。在对话中通过 `@using-architect` 即可唤醒架构体系。

### Codex CLI / App
在 Codex 插件目录建立软链接或拷贝至 `~/.codex/skills/`：
```bash
ln -s /path/to/architect_skill/skills/* ~/.codex/skills/
```

### Gemini CLI
作为扩展安装并保持上下文同步：
```bash
gemini extensions install /path/to/architect_skill
```

---

## 工程质量与自动化检查 (Testing & Verification)

本技能库将“技能编写”本身视为针对工程流程的测试驱动开发（TDD），内置了多层级自动化检验：

```bash
# 1. 语法编译检查
npm run compile

# 2. 静态规则扫描
npm run lint

# 3. 运行全套单元测试与技能规约测试 (44 项用例)
npm test
```

契约测试套件（`tests/test_skills_spec.py`）会严密校验：
1. 每个技能必须包含规范的 `SKILL.md`；
2. YAML Frontmatter 必须合法且命名符合 kebab-case 规范；
3. `description` 严格遵守 SDO 规约（必须以 `"Use when..."` 开头，仅声明触发时机）；
4. 技能文档内引用的所有相对模板与文件链接必须有效，杜绝死链。

---

## 贡献指南 (Contributing)

1. Fork 本仓库并基于 `main` 创建特性分支；
2. 遵循 `tests/test_skills_spec.py` 规约添加或修改技能；
3. 确保所有模板高内聚收纳在技能目录的 `templates/` 下；
4. 提交前必须执行并通过 `npm run compile && npm run lint && npm test`；
5. 发起 Pull Request 并清晰描述架构改动的业务背景与权衡点。

---

## 许可证 (License)

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
