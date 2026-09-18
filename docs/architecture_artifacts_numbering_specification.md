# 架构资产编号规范与全景画板呈现指南 (Architecture Artifacts Numbering Specification)

## 1. 架构产出物统一编号规范

为确保系统设计资产具备严格的可追溯性、确定性顺序以及工程化审计基准，系统确立了四层架构生命周期资产的唯一编号规则：`[阶段两位数字]-[序号两位数字]-[语义短名称].[扩展名]`。

### 1.1 Layer 1 · 业务与需求定义 (01-requirements)
- **`01-01-business-drivers.md`**：业务驱动力、商业目标与量化投资回报率 (Business Drivers & Goals)
- **`01-02-functional-requirements.md`**：系统核心用例规约与系统功能清单规约 (Functional Requirements & Use Cases)
- **`01-03-non-functional-requirements.md`**：质量属性场景化表达与非功能需求矩阵 (NFR Matrix & QAS)
- **`01-04-architecture-requirements-checklist.md`**：架构需求核对清单与双向映射表 (Architecture Requirements Checklist, ARC)
- **`01-05-constraints-and-assumptions.md`**：业务与技术硬约束、假设失效触发预案与系统不变量 (Constraints & Invariants)

### 1.2 Layer 2 · 概念与逻辑架构设计 (02-architecture-design)
- **`02-01-system-overview.md`**：系统架构总览、Level-0 黑盒边界与交互矩阵 (System Overview & Context)
- **`02-02-architecture-overview-diagram.md`**：IBM 规范 5 层架构全景概览图 (5-Layer AOD)
- **`02-03-c4-context.mmd` / `02-03-c4-context.md`**：C4 System Context 系统上下文边界拓扑图
- **`02-04-component-model.md`**：逻辑与物理组件模型、Provided/Required 接口契约与数据所有权 (Component Model, CM)
- **`02-05-c4-container-overview.mmd`**：C4 Container 容器拓扑图
- **`02-06-conceptual-data-model.md`**：概念数据模型、实体关系与统一语言词典 (CDM & Ubiquitous Language)
- **`02-06-domain-logical-model.md`**：领域逻辑模型与核心实体关系图 (Domain Logical Model)
- **`02-07-sequence-and-dataflow.md`**：端到端关键交互时序与核心数据流向图 (Interaction Sequence & Data Flow)

### 1.3 Layer 3 · 物理工程权衡与边界强契约 (03-engineering-and-physics)
- **`03-01-operational-model.md`**：物理运行拓扑、节点规范卡片集与受控沙箱隔离区 (Operational Model, OM)
- **`03-02-deployment-architecture.md`**：部署拓扑、高可用容灾与基础设施编排 (Deployment Architecture)
- **`03-03-data-architecture.md`**：数据架构、持久化选型与冷热分级流转 (Data Architecture)
- **`03-04-observability-design.md`**：统一可观测性、分布式链路追踪与 SLO 告警设计 (Observability Design)
- **`03-05-failure-resilience-matrix.md`**：FMEA 故障模式影响分析与容灾矩阵 (Failure Resilience Matrix)
- **`03-06-interface-contracts-overview.md`**：系统边界强契约与接口规约概览 (Interface Contracts Overview)
- **`03-07-openapi.yaml`**：OpenAPI 3.0 标准接口规约契约 (OpenAPI Specification)
- **`03-08-adrs/`**：架构决策记录集 (Architecture Decision Records)
  - `03-08-00-adr-index.md`：ADR 决策全景索引与状态总览
  - `03-08-01-ADR-001-*.md`：第 1 项核心决策记录
  - `03-08-02-ADR-002-*.md`：第 2 项核心决策记录

### 1.4 Layer 4 · 交付实施、组织阵型与工程围栏 (04-delivery-and-organization)
- **`04-01-organization-structure.md`**：康威定律对齐、团队拓扑与逆康威组织阵型 (Organization Structure)
- **`04-02-estimation-and-plan.md`**：工作量科学估算与敏捷交付里程碑 (Estimation & Delivery Plan)
- **`04-03-first-step-poc.md`**：垂直穿透破冰切片验证与破坏性混沌实验 (First-Step PoC Charter)
- **`04-04-walking-skeleton-spec.json`**：Walking Skeleton 自动化物理工程骨架生成规约 (Scaffold Spec)
- **`04-05-agent-rules.md`**：AI 与开发者执行纪律、架构依赖约束与安全围栏 (Engineering Guardrails)

---

## 2. 交互式架构画板 (Architecture Board) 呈现机制

画板采用单文件离线自包含 HTML (`architecture_board.html`) 编译机制：

1. **严格按编号升序显示**：
   - 左侧侧边栏自动根据输出物编号（`01-01` -> `04-05`）进行升序排布，杜绝乱序罗列；
   - 自动聚合至对应层级分组（Layer 1 业务需求、Layer 2 逻辑设计、Layer 3 物理工程、Layer 4 交付组织）。
2. **多模态视图联动切换**：
   - **架构拓扑视图 (Diagram View)**：针对包含 Mermaid 的工件，自动编译为高清 SVG，内置 `svg-pan-zoom` 交互引擎，支持滚轮缩放、鼠标抓取平移、一键居中自适应、深浅主题无缝切换与高清 SVG 导出；
   - **设计规约正文视图 (Document Spec View)**：针对需求矩阵、表格、不变量、ADR、OpenAPI 规约等文档，集成 Markdown 阅读排版，方便架构评审人一站式审查；
   - **快捷顺序浏览**：支持底部“上一个 / 下一个”按键以及键盘左右方向键（`ArrowLeft` / `ArrowRight`）顺次切换阅读。
