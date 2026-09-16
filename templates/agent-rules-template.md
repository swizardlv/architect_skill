# Vibe Coding 架构边界与防跑偏守则 (.agent-rules)

> **核心警示**：本代码库由架构师预先锚定了确定性工程骨架与接口契约。任何 AI 辅助编码助手（如 Cursor、Windsurf、Claude Code 等）在执行代码编写或重构时，**必须严格遵守以下三大架构红线与执行规范，违者视为产生致命架构漂移**。

---

## 一、三大不可逾越架构红线 (Three Immutable Redlines)

### 1. 只读契约目录红线 (Read-Only Contract Directory)
- **绝对只读路径**：
  - `docs/architecture/`（所有架构设计文档、C4 视图、ADR 记录）
  - `04-contracts/` 或 `src/contracts/`（OpenAPI Spec、Protobuf、JSON Schema 定义）
  - `src/domain/types/` 或 `src/domain/interfaces/`（强类型基准接口与实体定义）
  - `src/ports/`（核心六边形抽象端口定义）
- **铁律**：下游编码只能面向上述接口与契约编写具体实现，**严禁为了让代码跑通而私自篡改、删减或放宽接口签名与字段定义**。如需改动契约，必须回退至架构状态机重新发起评审。

### 2. 单向依赖倒置红线 (Strict Dependency Inversion)
- **依赖方向单向性**：
  - `domain/`（领域模型层）必须保持纯净，**严禁导入任何具体的框架、数据库 SDK、ORM 或网络适配器**（例如严禁在 domain 中导入 `fastapi`, `sqlalchemy`, `requests`, `aiohttp` 等）。
  - 所有外部能力（存储、外部 API、消息队列、模型调用）必须通过 `ports/` 声明的抽象接口进行依赖倒置注入。
  - `adapters/` 和 `infrastructure/` 只能单向依赖 `domain/` 和 `ports/`，内层核心绝对不可感知外层实现细节。

### 3. 测试沙箱自检闭环红线 (Closed-Loop Test Verification)
- **先验证后提交**：
  - 在向用户提交代码或标记任务完成前，必须在本地沙箱环境内依次通过：
    1. 静态代码分析与代码格式检查：`npm run lint` 或 `ruff check .`
    2. 严格静态类型检查：`npm run typecheck` 或 `mypy .`
    3. 自动化单元测试回归：`npm test` 或 `pytest`
- **严禁修改既有测试掩盖错误**：
  - 若代码改动导致既有单元测试或契约校验失败，**严禁私自放宽测试断言或删除测试用例**。测试失败意味着业务实现逻辑存在缺陷，必须修正实现直至所有测试通过。

---

## 二、允许编码与扩展的槽位 (Permitted Implementation Slots)

AI 编码助手仅允许在以下限定槽位开展工作：
1. **适配器实现层**：`src/adapters/`（例如数据库持久化实现、三方服务 Client 封装、HTTP Handler 等）。
2. **标有特定占位符的代码段**：明确包含 `# TODO: [VibeCoding Slot]` 或 `// TODO: [VibeCoding Slot]` 的具体函数体与业务流编排段落。
3. **测试用例编写**：`tests/`（新增覆盖新功能的单元测试与集成测试用例）。

---

## 三、故障应对与负向反思原则 (Failure & Reflection)

1. **拒绝无脑重复重试**：
   - 如果连续两次出现相同的编译错误或测试断言失败，严禁使用微调变量名等敷衍方式进行第三次盲目尝试。
   - 必须记录已证伪的错误路径，反思根因，并尝试推翻上一轮假设后提出全新修复逻辑。
2. **行级精确锚定**：
   - 优先使用带上下文锚点的行级精准 Patch 修改，避免整文件重写导致不可逆的代码丢失与行号偏移。
