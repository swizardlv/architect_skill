# Constraints & Invariants

## 1. 系统核心不变量
- 状态单向演进，禁止未定义回滚
- 只读契约目录禁止直接写
- Domain 层严禁反向依赖外部适配器
