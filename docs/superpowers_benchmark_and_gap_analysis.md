# 对标 obra/superpowers：专业级 Agentic Skill 仓库架构分析与改造方案

## 一、 背景与对标初衷

用户指出当前架构技能库存在组织形式不够标准的问题，要求深入学习业界标杆项目 `https://github.com/obra/superpowers`。

`superpowers` 是当前业内在 Agentic Skills 规范化、开发方法论与工具链编排领域的标杆开源项目。通过深度拆解其代码拓扑、规约定义与执行链路，我们发现了专业 Agent 技能库与传统文档堆砌型仓库之间的根本性代差。

---

## 二、 obra/superpowers 核心架构与哲学拆解

### 1. 核心设计哲学
- **规范标准遵循**：严格遵循 [agentskills.io](https://agentskills.io/specification) 规约。
- **高内聚自治的微内核 Skill 封装**：每一个 Skill 是一个自治目录（`skills/<skill-name>/`），核心包含 `SKILL.md`，辅以自洽的 `scripts/`、`references/` 与 `templates/`。
- **SDO（Skill Discovery Optimization，技能发现优化）**：
  - Frontmatter 中的 `description` 严格遵守 **“只声明何时触发（Use when...），绝不总结内部操作流”** 的黄金法则。
  - 原因：实测证明，若在 description 中总结了工作流，Agent 会直接依赖 description 产生捷径幻觉，跳过阅读 `SKILL.md` 全文，造成流程断裂。
- **硬性执行门禁（Hard Gates & Red Flags）**：
  - 用 `<HARD-GATE>`、`<EXTREMELY-IMPORTANT>` 封死 Agent 跳过流程的可能。
  - 详细的“心智红线对照表（Red Flags Table）”，将 Agent 偷懒的典型借口（如“这只是个简单问题”、“我先探查下代码再用技能”）一一封堵。
- **自举调度引导（Self-Bootstrapping via using-superpowers）**：
  - 拥有核心根引导技能 `using-superpowers`，制定全局激活优先级。
  - 配合 `hooks/session-start` 在会话开始时将引导规约注入上下文，使得 Agent 在第一回合交互中就能准确路由。
- **多平台无缝分发支持**：
  - 支持 Claude Code、Antigravity、Codex、Gemini CLI、Cursor、Hermes 等多运行端。
- **TDD 驱动技能与自动化规约扫描**：
  - 技能本身的编写被视作针对流程文档的 TDD。
  - 包含完善的 `tests/`，包含 shell-lint、manifest 校验、Frontmatter 校验等。

---

## 三、 当前 architect_skill 仓库与标杆的差距分析（Gap Analysis）

| 维度 | obra/superpowers 标杆模式 | 当前 architect_skill 现状 | 差距诊断与危害 |
| :--- | :--- | :--- | :--- |
| **目录组织形态** | 每个技能独立成目录：`skills/<name>/SKILL.md`，扁平且标准化。 | 按阶段切分子目录：`skills/01_grounding/*.md`，每个文件仅是裸 Markdown。 | 主流 Agent 运行环境（如 Antigravity / Claude）仅将含有 `SKILL.md` 的目录识别为可调用技能；当前裸 md 无法作为独立 Skill 被系统索引。 |
| **元数据与发现 (SDO)** | 拥有标准 YAML Frontmatter（`name` + `description: Use when...`），符合 SDO 规约。 | 绝大部分 Markdown 缺失 Frontmatter，或者 description 混合了功能概括。 | Agent 无法在上下文初始扫描阶段命中该技能，只能依靠主控提示词长篇硬塞。 |
| **资源协同与内聚** | 技能专用的参考资料放 `references/`，专用脚本放 `scripts/`，专用模板放同级。 | 模板全部散落在项目根目录 `templates/`（20多个文件混杂），与具体技能割裂。 | 认知负载高，技能与模板解耦过头，调用技能时需要穿越多个目录层级找模板。 |
| **调度与自举机制** | 拥有 `skills/using-superpowers/SKILL.md`，配合 `hooks/session-start` 自动注入。 | 仅有 Python 脚本驱动的 FSM 运行器和根目录脚本，缺乏纯 Agent 视角的自举引导 Skill。 | 使得外部调用容易滑向“改动脚本跑测试”的歧途，脱离了“Agent 读 Skill 自主执行”的本质。 |
| **质量门禁与自查** | 具备 `<HARD-GATE>` 与直击要害的 Red Flags 反思表格，明确路径分流（Spike/Bounded/Architectural）。 | 仅有常规步骤列表，缺乏强制阻断门禁和针对 Agent 常见走捷径思维的封堵机制。 | Agent 容易在没有人类架构师确认的情况下自行跳步、假装已设计完毕。 |
| **工程检验与验证** | 具备 `npm test` 对 Shell、技能文件格式、依赖的自动化 Lint 与格式契约检查。 | 仅对少数 Python 脚本执行编译和单元测试，未对 Markdown 技能的合规性建立检查。 | 容易出现坏链、YAML 格式损坏、Markdown Mermaid 解析报错等低级问题。 |

---

## 四、 重构演进路线与实施规划

为了将 `architect_skill` 升级为符合行业最高标准的专业 Agentic Skills 框架，我们制定以下四阶段重构方案：

### 阶段一：建立规范体系与自举核心
1. **建立根引导技能 `skills/using-architect/SKILL.md`**：
   - 确立“架构需求未明前，严禁越过架构技能直接编码”的总原则；
   - 制定分级路径（Spike / Standard-Architecture / Enterprise-Governance）；
   - 制定 Red Flags 认知阻断表。
2. **构建跨平台 SessionStart Hook（`hooks/`）**：
   - 适配 Antigravity / Claude Code / Codex 等平台的 session-start 机制，注入自举指引。

### 阶段二：重塑独立微内核技能目录结构
将现有的平铺 md 文件全部升级为标准的独立技能目录：
```text
skills/
├── using-architect/
│   └── SKILL.md
├── architect-grounding/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── structural-modeling/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── contracts-and-decisions/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── architecture-execution/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── architecture-audit-and-governance/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
└── architecture-polisher/
    ├── SKILL.md
    └── scripts/
```
或者保留细粒度原子技能，例如：
- `skills/distill-business-goals/SKILL.md`
- `skills/synthesize-architecture-overview/SKILL.md`
- `skills/derive-component-model/SKILL.md`
- `skills/derive-operational-model/SKILL.md`
- `skills/record-architecture-decision/SKILL.md`
- `skills/arb-review-gate/SKILL.md`
每一个都具备标准的 YAML Frontmatter，遵循 SDO 原则。

### 阶段三：内聚模板与参考资料
- 将根目录 `templates/` 下与特定技能绑定的模板，按高内聚原则迁移至对应 Skill 目录的 `templates/` 或 `references/`；
- 通用共享模板在根目录保留索引，避免技能散落。

### 阶段四：工程测试与规范校验器
- 编写 `tests/test_skills_spec.py`：自动遍历所有 `skills/*/SKILL.md`，验证：
  1. YAML Frontmatter 是否存在且合法；
  2. `name` 是否与目录名一致且只含小写字母和连字符；
  3. `description` 是否以 "Use when..." 开头且不超出字符上限；
  4. 引用的本地文件链接是否存在（死链检测）；
- 接入 `package.json` 的 `npm run lint` 与 `npm test`，确保提交前强行验证通过。
