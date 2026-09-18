#!/usr/bin/env python3
"""架构设计生命周期主控启动入口脚本 (run.py).

提供交互式与批处理命令行界面，用于驱动架构有限状态机推进、门禁检查与人工审批。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# 将当前目录和 scripts 目录加入 Python 搜索路径
CURRENT_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = CURRENT_DIR / "scripts"
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrate_architecture_lifecycle import (  # noqa: E402
    ArchitectureLifecycleFSM,
    FSMState,
    GatekeeperError,
    ReviewRejectedError,
    StateTransitionError,
)
from render_architecture_board import render_board  # noqa: E402


def print_banner() -> None:
    """打印终端启动横幅."""
    banner = """
======================================================================
       Architecture Lifecycle Orchestration Engine (Deterministic FSM)
       Deterministic Shell + Stochastic Core | 架构状态机驱动引擎
======================================================================
"""
    print(banner)


def generate_sample_assets(fsm: ArchitectureLifecycleFSM) -> None:
    """生成整套标准架构样本资产，以便进行端到端全链路验证."""
    ws = fsm.workspace_root
    fsm.ensure_workspace_directories()

    def find_template(name: str) -> Path | None:
        for p in (fsm.repo_root / "skills").rglob(name):
            if p.is_file():
                return p
        return None

    def write_file(rel_path: str, content: str) -> None:
        p = ws / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content.strip() + "\n", encoding="utf-8")

    # 1. 01-requirements/ (GRILLING & GROUNDING 门禁资产)
    write_file(
        "01-requirements/business-drivers.md",
        "# Business Drivers & Goals\n\n## 1. 核心业务驱动力\n- 打造确定性物理围栏与双环架构控制引擎\n- 解决传统 AI 编程助手随意越界破坏架构的痛点\n\n## 2. 投资回报与量化目标\n- 任务执行成功率 >= 95%\n- 架构单向推进零回滚",
    )
    write_file(
        "01-requirements/functional-requirements.md",
        "# Functional Requirements\n\n## 1. 核心用例规约 (Use Cases)\n- UC-01: 架构生命周期 FSM 确定性推进\n- UC-02: 人机交互审批卡点 (HITL)\n\n## 2. 功能需求规约清单\n### FR-01: 状态机推进与门禁自检\n系统必须提供单向状态推进能力，在推进前自动校验当前阶段的必需资产与语法完整性。\n\n### FR-02: 交互式审批与打回流转\n支持技术评审人签署批准或打回意见。\n\n### FR-03: 自动化代码骨架生成\n自动生成符合六边形架构的物理目录与自动化测试套件。",
    )
    write_file(
        "01-requirements/non-functional-requirements.md",
        "# Non-Functional Requirements (NFR Matrix)\n\n| 质量属性 | 指标定义 | SLA 目标 | 验证手段 |\n| :--- | :--- | :--- | :--- |\n| 确定性 | 状态跃迁严格单向 | 100% | 单元测试 |\n| 响应延迟 | 状态跃迁判定 | < 50ms | 基准测试 |\n| 安全防护 | 契约目录只读保护 | 100% | 沙箱权限 |",
    )
    write_file(
        "01-requirements/architecture-requirements-checklist.md",
        "# Architecture Requirements Checklist (ARC)\n\n| 需求编号 | 质量属性类别 | 量化设计指标 | 验证状态 |\n| :--- | :--- | :--- | :--- |\n| ARC-01 | 架构确定性 | 状态单向跃迁且无非法回滚 | 已实现 |\n| ARC-02 | 人机闭环 | 关键节点提供 HITL 审批阻断 | 已实现 |\n| ARC-03 | 物理接地 | 具备 Walking Skeleton 与冒烟测试 | 已实现 |",
    )
    write_file(
        "01-requirements/constraints-and-assumptions.md",
        "# Constraints & Invariants\n\n## 1. 系统核心不变量\n- 状态单向演进，禁止未定义回滚\n- 只读契约目录禁止直接写\n- Domain 层严禁反向依赖外部适配器",
    )

    # 2. 02-architecture-design/ (MODELING 门禁资产)
    write_file(
        "02-architecture-design/system-overview.md",
        "# System Architecture Overview\n\n系统采用双环控制架构：确定性外壳（Deterministic Shell）包裹概率推理内核（Stochastic Core），保证软件演进受控可信。",
    )

    aod_code = """# Architecture Overview Diagram (5-Layer AOD)
```mermaid
flowchart TD
    subgraph L1 ["接入与通道层"]
        CLI["CLI 客户端"]
    end
    subgraph L2 ["安全与守卫层"]
        Guard["鉴权与参数校验"]
    end
    subgraph L3 ["认知控制平面"]
        FSM["架构状态机编排引擎"]
    end
    subgraph L4 ["执行与网关层"]
        Gateway["模型与外部工具网关"]
    end
    subgraph L5 ["持久化层"]
        Storage["状态与元数据存储"]
    end
    L1 --> L2 --> L3 --> L4 --> L5
```
"""
    write_file("02-architecture-design/architecture-overview-diagram.md", aod_code)

    cm_code = """# Component Model
```mermaid
graph TD
    CLI["CLI Gateway"] --> FSM["FSM Orchestrator"]
    FSM --> Port["Storage Port"]
    Port --> Adapter["Memory/DB Adapter"]
```
"""
    write_file("02-architecture-design/component-model.md", cm_code)

    c4_context_code = """graph TB
    classDef personStyle fill:#f0fdfa,stroke:#0d9488,stroke-width:2px,color:#134e4a;
    classDef coreStyle fill:#eff6ff,stroke:#2563eb,stroke-width:3px,color:#1e3a8a;
    subgraph Users ["参与角色"]
        dev["👤 研发工程师"]:::personStyle
    end
    subgraph Boundary ["目标系统"]
        core["⚙️ 架构生命周期控制引擎"]:::coreStyle
    end
    dev --> core
"""
    write_file("02-architecture-design/c4-context.mmd", c4_context_code)

    c4_container_code = """graph TB
    cli["CLI Gateway"] --> fsm["FSM Engine"]
    fsm --> db[("State Storage")]
"""
    write_file("02-architecture-design/c4-container-overview.mmd", c4_container_code)

    domain_md_code = """# Domain Logical Model
```mermaid
stateDiagram-v2
    [*] --> INIT
    INIT --> GRILLING: START
    GRILLING --> GROUNDING: APPROVE
    GROUNDING --> MODELING: VALIDATED
    MODELING --> CONTRACTS: VALIDATED
    CONTRACTS --> SCAFFOLDING: APPROVE
    SCAFFOLDING --> FINALIZED: SKELETON_INITIALIZED
    FINALIZED --> [*]
```
"""
    write_file("02-architecture-design/domain-logical-model.md", domain_md_code)

    # 3. 03-engineering-and-physics/ (CONTRACTS 门禁资产)
    write_file(
        "03-engineering-and-physics/operational-model.md",
        "# Operational Model\n\n系统采用多环境容器化部署，支持本地单机验证与云原生 Kubernetes 编排运行。",
    )
    write_file(
        "03-engineering-and-physics/deployment-architecture.md",
        "# Deployment Architecture\n\n```mermaid\ngraph LR\n Client --> Gateway --> ServicePool\n```",
    )
    write_file(
        "03-engineering-and-physics/data-architecture.md",
        "# Data Architecture\n\n状态数据通过强一致事务写入关系型库，工件全量沉淀在对象存储或本地仓库。",
    )
    write_file(
        "03-engineering-and-physics/observability-design.md",
        "# Observability Design\n\n集成 OpenTelemetry 链路追踪，记录所有状态流转与门禁执行日志。",
    )
    write_file(
        "03-engineering-and-physics/failure-resilience-matrix.md",
        "# Failure Resilience Matrix (FMEA)\n\n| 故障场景 | 影响级别 | 容灾策略 | 恢复时效 |\n| :--- | :--- | :--- | :--- |\n| 进程意外崩溃 | 中 | 从持久化 .state.json 自动恢复 | < 1s |\n| 门禁未达成 | 低 | 确定性拦截并提示修复 | 即时 |",
    )
    write_file(
        "03-engineering-and-physics/adrs/adr-index.md",
        "# Architecture Decision Records\n\n- [ADR-001: 确定性状态机外壳](ADR-001-fsm-shell.md)",
    )
    write_file(
        "03-engineering-and-physics/adrs/ADR-001-fsm-shell.md",
        "# ADR-001: 确定性状态机外壳设计\n\n## 状态\nACCEPTED\n\n## 决定\n采用有限状态机严格控制系统架构推进。",
    )
    openapi_content = """openapi: 3.1.0
info:
  title: Architecture Lifecycle API
  version: 1.0.0
paths:
  /api/v1/status:
    get:
      summary: 获取当前架构生命周期状态
      responses:
        '200':
          description: OK
"""
    write_file("03-engineering-and-physics/contracts/openapi.yaml", openapi_content)
    write_file(
        "03-engineering-and-physics/contracts/interface-contracts-overview.md",
        "# Interface Contracts Overview\n\n定义了 OpenAPI 3.1 规格的外部 REST 通信接口与内部服务协议。",
    )

    # 4. 04-delivery-and-organization/ & .agent-rules.md (SCAFFOLDING 门禁资产)
    agent_rules = """# Agent Rules & Boundary Guardrails
- 严格遵循六边形架构边界规范
- 提交前必须执行编译与自动化测试
"""
    write_file(".agent-rules.md", agent_rules)
    if not (fsm.repo_root / ".agent-rules.md").exists():
        (fsm.repo_root / ".agent-rules.md").write_text(agent_rules, encoding="utf-8")

    write_file(
        "04-delivery-and-organization/organization-structure.md",
        "# Organization Structure\n\n开发团队采用纵向微团队编制，分为核心架构师组与领域实施组。",
    )
    write_file(
        "04-delivery-and-organization/estimation-and-plan.md",
        "# Estimation & Delivery Plan\n\n分为 M0 破冰骨架、M1 核心能力、M2 加固集成 3 个迭代周期。",
    )
    write_file(
        "04-delivery-and-organization/first-step-poc.md",
        "# First Step PoC\n\n验证状态机在受控沙箱中的单向跃迁与门禁拦截能力。",
    )

    target_base = fsm.workspace_root.parent.parent
    skeleton_spec = {
        "skeleton_version": "1.0.0",
        "architecture_pattern": "Hexagonal",
        "directories": ["src/domain", "src/ports", "src/adapters", "src/services", "tests"],
        "immutable_paths": ["docs/architecture", "src/ports"],
        "rules_file": ".agent-rules.md",
    }
    write_file(
        "04-delivery-and-organization/walking-skeleton-spec.json",
        json.dumps(skeleton_spec, ensure_ascii=False, indent=2),
    )

    # 5. 确保骨架物理目录与测试就绪
    try:
        from scaffold_walking_skeleton import generate_walking_skeleton
        generate_walking_skeleton(target_base)
    except Exception:
        for d in ["src/domain", "src/ports", "src/adapters", "src/services", "tests"]:
            (target_base / d).mkdir(parents=True, exist_ok=True)

    print("[成功] 演示架构资产已生成至工作区，可直接进行全链路测试。")



def run_interactive(fsm: ArchitectureLifecycleFSM, auto_approve: bool = False) -> None:
    """运行交互式推进循环."""
    print(f"[当前状态] {fsm.current_state.value}")
    report = fsm.get_status_report()
    print(f"[阶段说明] {report['description']}")

    while fsm.current_state != FSMState.FINALIZED:
        print("\n" + "-" * 60)
        print(f"正在准备从当前状态推进: {fsm.current_state.value}")

        # 检查门禁
        if fsm.current_state != FSMState.INIT:
            gate_res = fsm.validate_gatekeeper(fsm.current_state)
            print(f"门禁状态: {gate_res.summary()}")
            if not gate_res.passed:
                print(f"[拦截] 无法跃迁：请先补充所需资产文件后重试。")
                break

        # 人类介入检查
        prompt = fsm.get_hitl_prompt(fsm.current_state)
        approved = False
        feedback = ""

        if prompt is not None:
            print(f"\n[HITL 人机审核卡点] {prompt}")
            if auto_approve:
                print("[自动放行] 检测到 --auto-approve 标志，直接签署通过。")
                approved = True
            else:
                user_input = input("请输入审批意见 [Y: 批准 / N: 打回并输入理由]: ").strip()
                if user_input.lower() in ("y", "yes", ""):
                    approved = True
                else:
                    approved = False
                    feedback = input("请输入打回原因/修改诉求: ").strip() or "未附带详细说明"

        try:
            new_state, msg = fsm.advance(
                hitl_approved=approved,
                reviewer_feedback=feedback,
            )
            print(f"[推进成功] {msg}")
        except ReviewRejectedError as r_err:
            print(f"[审批打回] {r_err}")
            break
        except GatekeeperError as g_err:
            print(f"[门禁拦截] {g_err}")
            break
        except StateTransitionError as s_err:
            print(f"[流转错误] {s_err}")
            break

    if fsm.current_state == FSMState.FINALIZED:
        print("\n======================================================================")
        print(" [达成] 架构生命周期已推进至终态 FINALIZED，全部基线与围栏锁定就绪！")
        print("======================================================================\n")


def main() -> None:
    """CLI 主入口函数."""
    parser = argparse.ArgumentParser(
        description="架构设计生命周期主控引擎 (Deterministic FSM Orchestrator)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--status", action="store_true", help="显示当前架构状态与门禁检查报告")
    parser.add_argument("--step", action="store_true", help="单步执行一次状态跃迁")
    parser.add_argument("--auto-approve", action="store_true", help="自动批准人机卡点 (HITL)")
    parser.add_argument("--reset", action="store_true", help="重置当前状态为 INIT 并清空历史状态文件")
    parser.add_argument("--init-sample-assets", action="store_true", help="快速生成符合规范的演示架构资产")
    parser.add_argument("--render-board", action="store_true", help="将 02-models/ 图表编译为自包含交互式 HTML 画板")
    parser.add_argument("--workspace", type=str, default=None, help="自定义架构工作区目录路径")

    args = parser.parse_args()

    print_banner()

    fsm = ArchitectureLifecycleFSM(workspace_root=args.workspace)

    if args.render_board:
        out_html = render_board(fsm.workspace_root)
        print(f"[画板生成成功] 自包含交互式架构全景画板已生成至:\nfile://{out_html}")
        return

    if args.reset:
        if fsm.state_file.exists():
            fsm.state_file.unlink()
        fsm.resume_or_init()
        print("[重置完成] 状态机已恢复为初始状态: INIT")
        return

    if args.init_sample_assets:
        generate_sample_assets(fsm)
        return

    if args.status:
        report = fsm.get_status_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if args.step:
        prompt = fsm.get_hitl_prompt(fsm.current_state)
        approved = args.auto_approve
        feedback = ""
        if prompt and not approved:
            choice = input(f"[HITL 卡点: {prompt}]\n是否批准? [y/N]: ").strip().lower()
            approved = (choice in ("y", "yes"))
            if not approved:
                feedback = input("输入打回意见: ").strip()

        try:
            new_state, msg = fsm.advance(hitl_approved=approved, reviewer_feedback=feedback)
            print(f"[推进成功] {msg}")
        except Exception as e:
            print(f"[推进失败] {e}", file=sys.stderr)
            sys.exit(1)
        return

    # 默认模式：交互式推演
    run_interactive(fsm, auto_approve=args.auto_approve)


if __name__ == "__main__":
    main()
