# 架构决策记录索引 (Architectural Decision Records Index)

## 1. 架构决策全景总览 (ADR Decision Radar)

| 决策编号 | 决策主题 | 当前状态 | 核心权衡要素 (Trade-offs) | 影响范围 | 落地遵从性防线 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[ADR-001](./ADR-001-fsm-shell.md)** | 采用基于确定性有限状态机 (FSM) 的架构生命周期编排器 | **已接受 (Accepted)** | 保证架构阶段推进确定性与门禁防线 vs 状态流转开发维护成本 | `orchestrate_architecture_lifecycle.py`, Gatekeeper | `tests/test_fsm_orchestrator.py` 单测全覆盖 |

---

## 2. 治理机制与生命周期流转 (Governance Lifecycle)
所有架构决策均遵循 IBM Architecture Thinking 标准生命周期状态机管理：
- **提议 (Proposed)**: 产生于架构探索阶段，需给出量化指标与至少 2~3 个可行备选方案。
- **已接受 (Accepted)**: 经过架构委员会评审合入，作为工程开发必须遵从的不可违背法则。
- **已废弃 (Deprecated)**: 随着业务或技术基座演进不再适用。
- **被取代 (Superseded by ADR-XXX)**: 历史决策不直接修改，必须通过新 ADR 继承并声明取代。

---

## 3. 架构四大支柱闭环关联 (Four Pillars Closure)
- **AOD (全局概览)**: 统领架构技能的运行边界与高阶交互信息流。
- **CM (组件模型)**: 解耦编排器、门禁守护者、渲染器与打磨引擎的边界与契约。
- **OM (运行模型)**: 规范运行环境、CPU 资源分配与文件系统持久化拓扑。
- **AD/ADR (决策法典)**: 记录所有技术重大抉择的权衡依据、负向妥协与三级缓解防线。

---

## 4. 后续 ADR 规划候选池 (Future Backlog)
- **ADR-002**: 架构看板多图表动态嵌入与 Mermaid 双引擎回退机制
- **ADR-003**: 跨工作区测试沙箱的并发隔离与自愈恢复策略