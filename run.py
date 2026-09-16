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

# 将当前目录和 00_orchestrator 目录加入 Python 搜索路径
CURRENT_DIR = Path(__file__).parent.resolve()
ORCHESTRATOR_DIR = CURRENT_DIR / "skills" / "00_orchestrator"
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(ORCHESTRATOR_DIR))

from orchestrate_architecture_lifecycle import (  # noqa: E402
    ArchitectureLifecycleFSM,
    FSMState,
    GatekeeperError,
    ReviewRejectedError,
    StateTransitionError,
)


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
    templates_dir = fsm.repo_root / "templates"
    fsm.ensure_workspace_directories()

    # 1. 00-grounding/grounding-spec.json
    grounding_json = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "status": "COMPLETED",
        "grounding_spec": {
            "project_name": "ai-assisted-coding-mesh",
            "business_driver": "解决传统 AI 编程助手随意重构代码破坏架构边界的痛点，通过确定性外壳提供物理围栏。",
            "core_invariants": [
                "状态单向跃迁，禁止未定义的回滚",
                "只读契约目录禁止直接修改",
                "domain 层严禁引入外部持久化或网络适配器",
            ],
            "nfr_targets": {
                "throughput_qps": "均值 500 QPS，峰值 2000 QPS",
                "p99_latency": "P95 < 200ms, P99 < 800ms",
                "rpo_rto": "RPO < 1m, RTO < 5m",
                "consistency_preference": "CP",
                "resource_budget": "单次任务 Token 消耗 <= 8,000",
            },
            "constraints": {
                "tech_stack_allowlist": ["Python 3.11+", "FastAPI", "SQLite", "Redis"],
                "ops_and_infrastructure": "独立容器沙箱、无公网直连写权限",
                "legacy_integrations": ["企业统一 IAM gRPC 接口", "Git 仓库 SSH 接口"],
            },
            "anti_goals": [
                "本期不做跨集群多活自动调度",
                "禁止引入未经验证的自主多智能体通信",
            ],
        },
    }
    (ws / "00-grounding" / "grounding-spec.json").write_text(
        json.dumps(grounding_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 2. 01-grounding/nfr-matrix.md & constraints-and-assumptions.md
    nfr_tmpl = templates_dir / "nfr-matrix-template.md"
    if nfr_tmpl.exists():
        (ws / "01-grounding" / "nfr-matrix.md").write_text(nfr_tmpl.read_text(encoding="utf-8"), encoding="utf-8")

    const_tmpl = templates_dir / "constraints-template.md"
    if const_tmpl.exists():
        (ws / "01-grounding" / "constraints-and-assumptions.md").write_text(
            const_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # 3. 02-models/
    c4_ctx = (
        fsm.repo_root / "skills" / "02_structural_modeling" / "generate_system_context.md"
    ).read_text(encoding="utf-8")
    (ws / "02-models" / "c4-context.mmd").write_text(
        "C4Context\ntitle System Context\nPerson(u, \"User\")\nSystem(s, \"Core System\")\nRel(u, s, \"Calls\")",
        encoding="utf-8",
    )

    domain_md = (
        fsm.repo_root / "skills" / "02_structural_modeling" / "derive_logical_domain_model.md"
    ).read_text(encoding="utf-8")
    (ws / "02-models" / "domain-logical-model.md").write_text(
        "# Domain Logical Model\n\n## 限界上下文与聚合根\n- ArchitectureJob (Aggregate Root)",
        encoding="utf-8",
    )

    (ws / "02-models" / "c4-container-overview.mmd").write_text(
        "C4Container\ntitle Container Diagram\nContainer(gw, \"Gateway\", \"FastAPI\")",
        encoding="utf-8",
    )

    # 4. 03-decisions & 04-contracts
    (ws / "03-decisions" / "adr-index.md").write_text(
        "# ADR Index\n\n- [ADR-001: 确定性状态机外壳与受限沙箱](ADR-001-fsm-shell.md)",
        encoding="utf-8",
    )

    adr_tmpl = templates_dir / "adr-template.md"
    if adr_tmpl.exists():
        (ws / "03-decisions" / "ADR-001-fsm-shell.md").write_text(
            adr_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    res_tmpl = templates_dir / "resilience-matrix-template.md"
    if res_tmpl.exists():
        (ws / "03-decisions" / "failure-resilience-matrix.md").write_text(
            res_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    openapi_content = """openapi: 3.1.0
info:
  title: Architecture Lifecycle API
  version: 1.0.0
paths:
  /api/v1/jobs:
    get:
      summary: 获取任务列表
      responses:
        '200':
          description: OK
"""
    (ws / "04-contracts" / "openapi.yaml").write_text(openapi_content, encoding="utf-8")

    # 5. 04-execution & .agent-rules.md
    agent_rules_tmpl = templates_dir / "agent-rules-template.md"
    if agent_rules_tmpl.exists():
        (fsm.repo_root / ".agent-rules.md").write_text(
            agent_rules_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    (ws / "04-execution" / "roadmap-and-first-step.md").write_text(
        "# Roadmap & First Step\n\n## Milestone 0: Tracer Bullet PoC\n跑通带超时的沙箱执行与补丁定位。",
        encoding="utf-8",
    )

    skeleton_spec = {
        "skeleton_version": "1.0.0",
        "architecture_pattern": "Hexagonal",
        "directories": ["src/domain", "src/ports", "src/adapters", "tests"],
        "immutable_paths": ["docs/architecture", "src/ports"],
        "rules_file": ".agent-rules.md",
    }
    (ws / "04-execution" / "walking-skeleton-spec.json").write_text(
        json.dumps(skeleton_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

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
    parser.add_argument("--workspace", type=str, default=None, help="自定义架构工作区目录路径")

    args = parser.parse_args()

    print_banner()

    fsm = ArchitectureLifecycleFSM(workspace_root=args.workspace)

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
