# 自动化架构合规扫描与防腐规约 (Architecture Conformance Specification)

> **治理视角**: 代码级架构防腐与 CI/CD 自动守卫 (Architecture as Tests & Conformance Gate)  
> **核心使命**: 将架构技能套件的组件模型（CM）与质量门禁契约转化为自动化架构测试用例，嵌入持续集成流水线，实行“违规即熔断（Break the Build）”，杜绝因随意的代码改动破坏生命周期状态机与纯本地无状态持久化防线。

---

## 1. 架构合规扫描策略概览 (Governance Policy Overview)

| 治理要素 | 规约配置与执行策略 |
| :--- | :--- |
| **CI/CD 触发时机** | **PR 第一道门禁 (Pull Request Gate)**：每次提交代码或合并分支时自动触发，全流程耗时 $\le$ 5 秒 |
| **构建拦截效力** | **违规即熔断 (Break the Build)**：凡检测到反向分层依赖、状态机私有属性非法越权修改，CI 立即强行中断 |
| **规则对齐模式** | **1:1 强映射**: 架构测试规则直接绑定组件模型（`COMP-01` 至 `COMP-03`）与架构决策（`ADR-001/002`） |
| **存量治理原则** | **基线冻结 (Freezing Baseline)**: 存量违规条目冻结在 `.architecture/frozen_baseline.json`，增量新代码实行零容忍拦截 |
| **技术实现工具** | **Python AST 静态解析 / Pytest Architecture Rules / npm audit / Safety CVE Scanner** |

---

## 2. 核心架构测试规则清单 (Architecture Test Rules & CM Mapping)

| 规则编号 | 规则名称与描述 | 关联组件/决策 | 扫描维度 | 拦截级别 | 预期校验行为 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ARCH-RULE-01` | **套件调度单向依赖校验** | `COMP-01 ~ COMP-03` | 分层与边界 | **致命 (Fatal - Break Build)** | 调度入口 `run.py` $\to$ `orchestrator` $\to$ `document_polisher` $\to$ `render_board`，严禁任何逆向调用 |
| `ARCH-RULE-02` | **全域无环依赖检测 (ADP)** | 全局模块切片 | 分层与边界 | **致命 (Fatal - Break Build)** | 基于 Python AST 构建依赖图，确保模块间无循环引用（DAG 拓扑） |
| `ARCH-RULE-03` | **状态持久化写入独占权防腐**| `COMP-01 / ADR-002` | 数据所有权 | **致命 (Fatal - Break Build)** | `state.json` 的写操作仅允许由 `LifecycleOrchestrator` 独占执行，严禁其他模块直接写入 |
| `ARCH-RULE-04` | **规约文档与业务代码物理隔离**| `COMP-02 / ADR-001` | 包结构与契约 | **严重 (Critical)** | 主代码库严禁混入具体业务实现代码，测试工程必须物理隔离于外部目录 |
| `ARCH-RULE-05` | **开源依赖协议与 CVE 阻断** | 全局依赖包 | 供应链安全 | **严重 (Critical)** | 阻断强传染性 GPL 依赖，阻断含有已知高危 CVE（CVSS $\ge$ 7.0）的第三方轮子 |

---

## 3. 架构单元测试代码化实现 (Architecture as Tests - Python AST)

```python
import ast
from pathlib import Path
import pytest

class TestArchitectureConformance:

    @pytest.fixture
    def repo_ast_graph(self):
        # 基于 Python AST 提取源码中的 import 依赖关系图
        root = Path(__file__).resolve().parent.parent
        imports = {}
        for py_file in root.glob("skills/**/*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
                module_name = py_file.stem
                imports[module_name] = [
                    node.names[0].name for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom)) and node.names
                ]
        return imports

    # 1. 强制单向分层依赖校验 (CM-001 到 CM-003)
    def test_polisher_must_not_depend_on_orchestrator(self, repo_ast_graph):
        polisher_deps = repo_ast_graph.get("document_polisher", [])
        assert "orchestrate_architecture_lifecycle" not in polisher_deps, \
            "COMP-02 门禁守护组件严禁反向依赖 COMP-01 调度引擎，必须保持纯函数独立性"

    # 2. 严禁循环依赖 (ADP 原则)
    def test_skills_modules_free_of_cycles(self, repo_ast_graph):
        # 拓扑排序检测有向环
        visited = set()
        rec_stack = set()
        def has_cycle(v):
            visited.add(v)
            rec_stack.add(v)
            for neighbor in repo_ast_graph.get(v, []):
                if neighbor in repo_ast_graph:
                    if neighbor not in visited:
                        if has_cycle(neighbor): return True
                    elif neighbor in rec_stack:
                        return True
            rec_stack.remove(v)
            return False
        assert not any(has_cycle(mod) for mod in repo_ast_graph if mod not in visited), \
            "架构扫描检出模块间存在循环依赖，违反无环依赖原则 (ADP)"
```

---

## 4. 架构特例豁免与时效台账 (Architecture Exceptions & Expiration Dates)

| 豁免编号 | 违背规则 | 豁免模块与代码路径 | 豁免业务理由 | 批准人 (Approver) | 到期失效日 (Expire Date) | 清偿进展 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EXCP-001` | `ARCH-RULE-03` | `tests/test_fsm_orchestrator.py` | 测试用例为了模拟磁盘损坏直接注入损坏的 JSON 文件 | 首席架构师 | **2026-11-30** | 重构为通过 Mock 接口注入 |
| `EXCP-002` | `ARCH-RULE-01` | `scripts/manage_test_workspaces.py` | 临时管理脚本为了简化操作直接引入了测试断言工具 | 质量总监 | **2026-10-15** | 待解耦为独立 CLI 插件 |

---

## 5. 基线冻结与架构健康度看板 (Baseline Freezing & Health Dashboard)

- **存量基线文件**: 位于 `.architecture/frozen_baseline.json`，锁定系统既有的 3 处存量遗留历史条目。
- **增量合规指标**: 增量提交代码违规熔断拦截率 = **100%**。
- **技术债务递减目标**: 伴随日常重构，基线违规条目每季度下调不低于 **30%**，直至清零。
- **本地开发者体验**: 集成 `pre-commit` Git 钩子，本地运行 `npm run lint` / `npm test` 在 100ms 内获得即时合规校验反馈。
