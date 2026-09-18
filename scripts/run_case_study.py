#!/usr/bin/env python3
"""端到端案例工作区与生命周期验证辅助工具 (run_case_study.py).

本脚本为通用工具，不硬编码任何具体业务案例内容。
它提供对测试工作区（默认为 ~/code/architect_skill_tests/<case_name>）的
目录初始化、版本快照归档、FSM 门禁校验、交互画板编译与质量评分能力。
具体的业务架构资产由 AI 架构师运用 skills/ 规范与模板动态生成。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = REPO_ROOT / "scripts"
POLISHER_DIR = REPO_ROOT / "skills" / "architecture-refinement" / "scripts"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(POLISHER_DIR))

from manage_test_workspaces import archive_case_workspace, update_cases_index_readme
from render_architecture_board import render_board
from document_polisher import ArchitectureDocumentPolisher


def ensure_case_workspace(case_dir: Path) -> None:
    """初始化案例工作区标准目录结构."""
    arch_dir = case_dir / "docs" / "architecture"
    src_dir = case_dir / "src"
    tests_dir = case_dir / "tests"

    for sub in [
        arch_dir / "01-grounding",
        arch_dir / "02-models",
        arch_dir / "03-decisions",
        arch_dir / "04-execution",
        src_dir / "domain",
        src_dir / "ports",
        src_dir / "adapters",
        tests_dir,
    ]:
        sub.mkdir(parents=True, exist_ok=True)


def evaluate_workspace(case_dir: Path) -> None:
    """执行交互画板编译与文档质量评分."""
    arch_dir = case_dir / "docs" / "architecture"
    if not arch_dir.exists():
        print(f"❌ 错误: 架构目录不存在: {arch_dir}")
        return

    print("\n🎨 [画板编译] 正在编译自包含离线交互架构画板...")
    try:
        html_board = render_board(arch_dir)
        print(f"   画板已成功生成: file://{html_board}")
    except Exception as e:
        print(f"   ⚠️ 画板生成异常: {e}")

    print("\n📋 [质量评估] 正在运行架构文档质量精细度审查 (document_polisher)...")
    polisher = ArchitectureDocumentPolisher(arch_dir)
    passed, reports = polisher.audit_workspace()
    avg_score = sum(r.score for r in reports) / len(reports) if reports else 0.0
    status_str = "通过 (PASS)" if passed else "需进一步打磨深化 (NEEDS REFINEMENT)"
    print(f"   已审查文档数: {len(reports)} 篇")
    print(f"   综合质量评分: {avg_score:.1f} 分 / 状态: {status_str}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="端到端案例工作区与生命周期验证辅助工具 (run_case_study.py)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("case_name", help="案例目录名称 (如 photo_magic_house)")
    parser.add_argument(
        "--base-dir",
        default=os.path.expanduser("~/code/architect_skill_tests"),
        help="测试基准目录 (默认: ~/code/architect_skill_tests)"
    )
    parser.add_argument(
        "--action",
        choices=["init", "audit", "archive", "all"],
        default="all",
        help="执行动作: init (仅建目录), audit (画板+质量审查), archive (快照归档), all (综合闭环流程)"
    )
    parser.add_argument("--no-archive", action="store_true", help="跳过对既有产物的自动归档")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)
    case_dir = base_dir / args.case_name

    print("\n" + "=" * 70)
    print(f"🛠️ [案例工具] 目标案例: {args.case_name}")
    print(f"📂 [工作路径] {case_dir}")
    print("=" * 70)

    if args.action in ("archive", "all") and not args.no_archive and case_dir.exists():
        print(f"\n📦 检测到既有案例资产，执行快照归档...")
        arch_path = archive_case_workspace(case_dir, base_dir)
        if arch_path:
            print(f"   已归档至: {arch_path.name}")

    if args.action in ("init", "all"):
        print(f"\n📁 确保案例标准目录体系就绪...")
        ensure_case_workspace(case_dir)

    if args.action in ("audit", "all"):
        evaluate_workspace(case_dir)

    # 同步索引
    update_cases_index_readme(base_dir)
    print(f"\n📑 测试目录 README.md 索引已同步。")


if __name__ == "__main__":
    main()
