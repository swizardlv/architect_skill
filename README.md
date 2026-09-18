# Architect Skill (专业级 AI 架构师技能库)

> An agentic skills framework & software architecture methodology for AI coding agents.

对标并吸纳业界标杆 [`obra/superpowers`](https://github.com/obra/superpowers) 与 [agentskills.io](https://agentskills.io/specification) 标准规约，为 Claude Code、Antigravity、Codex、Gemini CLI 等 AI 编码 Agent 提供一套高内聚、微内核化、自举式驱动的软件架构设计与工程治理方法论。

---

## 核心设计哲学

1. **先架构后编码 (Architecture Before Code)**：未经架构论证、非功能需求评估与质量属性约束的编码，是系统失控与架构退化的主因。
2. **微内核自治封装 (Self-Contained Skills)**：每一个架构技能是一个自治目录（`skills/<name>/`），核心包含规范的 `SKILL.md`（带 SDO YAML Frontmatter），附属模板放于专属 `templates/`，脚本放于 `scripts/`。
3. **SDO (Skill Discovery Optimization，技能发现优化)**：`description` 严格遵守以 `"Use when..."` 开头的触发契约，仅声明激活时机，避免 Agent 依赖概述产生跳步幻觉。
4. **硬性执行门禁与心智红线 (Hard Gates & Red Flags)**：设置强拦截规则，阻断 Agent 擅自跳过架构设计、假装已完成的偷懒倾向。
5. **双轨架构指标 (Dual-Track Architecture Requirements)**：不仅涵盖吞吐、并发与延迟等传统指标，更涵盖 Agent 时代的认知有效性（Cognitive Efficacy）、Token 经济学预算、安全围栏与确定性兜底。

---

## 技能库全景 (Skills Catalog)

```text
skills/
├── using-architect/                  # 自举引导元技能 (优先级、心智红线对照、路径分级与硬门禁)
│   └── SKILL.md
├── architecture-grounding/           # 架构需求锚定与度量 (商业愿景、NFR 矩阵、ARC 需求清单、约束编目)
│   ├── SKILL.md
│   └── templates/
├── architecture-overview/            # 架构全景与风格决策 (系统上下文图、AOD 分层大图、风格决策)
│   ├── SKILL.md
│   └── templates/
├── component-modeling/               # 组件模型与动态时序 (CM 组件边界、拓扑依赖、交互端口、时序与数据流)
│   ├── SKILL.md
│   └── templates/
├── operational-modeling/             # 运行模型与系统韧性 (物理部署节点、网络分区、故障韧性矩阵、可观测性)
│   ├── SKILL.md
│   └── templates/
├── conceptual-data-modeling/         # 概念数据模型与存储 (ER 实体图、物理 DDL 骨架、多模存储划分)
│   ├── SKILL.md
│   └── templates/
├── boundary-contracts/               # 系统边界契约 (RESTful API、异步事件载荷、防腐适配层)
│   ├── SKILL.md
│   └── templates/
├── architecture-decisions/           # 架构决策记录 (MADR 规范、AI 时代 6 大核心决策博弈)
│   ├── SKILL.md
│   └── templates/
├── architecture-execution/           # 架构交付与实证验证 (Walking Skeleton 骨架贯通、靶向 PoC、里程碑编排)
│   ├── SKILL.md
│   └── templates/
├── architecture-governance/          # 架构治理与评审 (ARB 评审网关、ATAM 效用树穿刺、合规扫描、技术债务台账)
│   ├── SKILL.md
│   └── templates/
└── architecture-refinement/          # 架构文档精修与看板 (格式审查排版脚本、交互式 HTML 画板渲染引擎)
    ├── SKILL.md
    └── scripts/
```

---

## 安装与多平台适配

### Antigravity
作为插件从本地或 Git 仓库安装：
```bash
agy plugin install /path/to/architect_skill
```
Antigravity 会自动执行 `hooks/session-start`，在每次会话启动、清屏或压缩时自动注入 `using-architect` 引导上下文。

### Claude Code
作为本地插件安装：
```bash
claude plugin add /path/to/architect_skill
```

### 其他平台 (Codex / Cursor / Gemini CLI)
支持直接挂载到各平台技能目录（如 `~/.agents/skills/` 或 `~/.gemini/antigravity-cli/skills/`）。

---

## 核心工作流与路径分级

面对工程需求时，首先明确任务路径等级：

1. **Spike 验证型**：技术可行性探针，输出轻量结论，不保留为生产代码；
2. **Bounded 局域型**：已有明确系统架构下的增量变更，局部补充组件契约或 ADR；
3. **Architectural 系统型**：全新系统、核心重构或引入非确定性 AI 能力，必须完整执行全套架构技能推导。

推导步骤：
```text
[using-architect]
       │
       ▼
[architecture-grounding] ──────► 产出 ARC、NFR 矩阵与硬约束
       │
       ▼
[architecture-overview]  ──────► 确立 System Context 与 AOD 分层大图
       │
       ▼
[component-modeling]     ──────► 细化组件模型 CM 与端到端时序流
       │
       ▼
[operational-modeling]   ──────► 制定物理运行模型 OM、网络分区与故障韧性矩阵
       │
       ▼
[conceptual-data-modeling] ────► 确立实体模型、生产级 DDL 与多模存储划分
       │
       ▼
[boundary-contracts]     ──────► 制定 OpenAPI / 异步事件契约
       │
       ▼
[architecture-decisions] ──────► 记录关键技术博弈 ADR
       │
       ▼
[architecture-execution] ──────► 编写 Walking Skeleton 骨架与 PoC 验证
       │
       ▼
[architecture-governance] ─────► 提交 ARB 评审门禁与 ATAM 效用树穿刺
       │
       ▼
[architecture-refinement] ─────► 自动化排版精修并生成交互式 HTML 架构看板
```

---

## 工程质量与自动化契约检查

本仓库内置严格的技能规约与代码质量自动化检查，对标工业级标准：

```bash
# 1. 语法与字节码编译检查
npm run compile

# 2. 代码与规范静态检查
npm run lint

# 3. 运行全套契约与功能测试 (含技能规范检查 tests/test_skills_spec.py)
npm test
```

测试套件将自动检查：
- 所有技能是否包含合法的 `SKILL.md`；
- YAML Frontmatter 是否合规且与目录名一致；
- `description` 是否遵守 SDO（以 `Use when...` 开头）；
- 文档内部引用的相对文件与模板是否存在（死链防护）。
