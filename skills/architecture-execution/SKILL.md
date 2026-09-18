---
name: architecture-execution
description: "Use when scaffolding walking skeletons, executing architectural proof-of-concepts (PoC), sequencing delivery milestones, or validating architectural assumptions with minimal code"
---

# Architecture Execution (架构交付与实证验证)

## 概述

未经实证检验的架构只是假说。架构交付技能负责将纸面架构快速转化为可运行、可量化验证的最小闭环系统。

通过**Walking Skeleton（端到端细垂直切片）**与**靶向 PoC（概念实证验证）**，我们在大规模工程展开前排查未知的技术卡点与外部 API 风险。

## 适用场景 (When to Use)

- 在开始大规模写业务逻辑之前，搭建端到端打通的最小骨架系统；
- 验证未知或高风险技术假设（如三方生图模型 API 的延迟、扣除配额与回调稳定性）；
- 规划系统交付里程碑（Milestones）与迭代切片；
- 建立工程代码规范、CI 门禁与自动化测试基线。

## 核心交付物与工具
 
 1. **物理代码骨架生成工具**：`scripts/scaffold_walking_skeleton.py`
    - 命令：`python3 skills/architecture-execution/scripts/scaffold_walking_skeleton.py <workspace_root> --run-test`
    - 作用：自动将组件模型与契约转化为六边形架构的 `domain/`, `ports/`, `adapters/`, `services/` 源码骨架与自动化集成测试 `tests/`，并直接跑通冒烟验证。
 2. **PoC 实验章程与评估报告**：[poc-charter-and-report-template.md](templates/poc-charter-and-report-template.md)
 3. **交付组织架构与里程碑规划**：[organization-and-plan-template.md](templates/organization-and-plan-template.md)


## 执行步骤与检查清单

### 步骤一：高风险假设提炼与靶向 PoC
- 识别系统最脆弱的假设（例如：“混元生图接口能否在 10 秒内完成去路人？返回的图片画质是否满足小程序要求？”）；
- 编写靶向 PoC 代码（严禁写死在架构技能库中，统一放置在测试工作区或探针脚本中）；
- 收集量化数据（P50/P90 耗时、成功率、错误类型），输出实证结论。

### 步骤二：Walking Skeleton（骨架贯通）搭建
- 实现从客户端 API -> 网关 -> 业务控制服务 -> 模拟/真实 Worker -> 数据库/缓存写回的极简端到端连通；
- 验证配置中心、日志记录与基础异常处理是否生效；
- 确保整个流水线能在本地或开发环境自动化拉起并跑通健康检查。

### 步骤三：垂直切片交付编排 (Vertical Slicing)
- 将系统划分为可独立验证的交付里程碑（M0: 基础底座与模型连通, M1: 核心图片处理链路, M2: 后台管理与风控配额, M3: 生产加固与灾备）；
- 每个里程碑均包含端到端的测试与演示标准，拒绝长期停留在水平切片（只写数据库或只画界面）。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
严禁将未经 PoC 检验的外部高风险第三方依赖直接定稿为生产选型。
Walking Skeleton 必须具备自动化冒烟测试（Smoke Test）用例，确保后续多人或多 Agent 并行开发时有明确的合流基线。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “PoC 直接写在架构主工程源码里，以后慢慢改” | 探针代码必须与生产主干隔离，验证完毕后提取结论，避免将临时实验代码带入生产。 |
| “先把所有表建好、界面画完再来连通接口” | 水平推进容易导致联调阶段出现大量阻塞性契约冲突，必须坚持垂直切片贯通。 |
