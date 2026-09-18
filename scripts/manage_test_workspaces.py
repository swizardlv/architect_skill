"""测试工作区管理与快照归档工具 (Manage Test Workspaces).

提供对 ~/code/architect_skill_tests/ 测试输出工作区的通用归档与索引维护能力。
不包含任何具体的业务案例硬编码，纯粹作为支持闭环演进的工具脚本。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def clean_legacy_directories(case_dir: Path) -> None:
    """清理历史遗留的废弃空目录 (仅当目录为空时清理)."""
    arch_root = case_dir / "docs" / "architecture"
    if not arch_root.exists():
        return
    legacy_dirs = [
        "00-grounding",
        "01-grounding",
        "02-models",
        "03-decisions",
        "04-contracts",
        "04-execution",
    ]
    for leg in legacy_dirs:
        leg_path = arch_root / leg
        if leg_path.exists() and leg_path.is_dir():
            # 仅当为空或仅包含空子目录时安全清理
            has_files = any(p.is_file() for p in leg_path.rglob("*"))
            if not has_files:
                shutil.rmtree(leg_path, ignore_errors=True)
                print(f"🧹 [自动清理] 清除历史遗留空目录: {leg_path.name}")


def archive_case_workspace(case_dir: Path, base_dir: Path) -> Path | None:
    """将既有案例目录完整快照归档至 .archive 目录."""
    if not case_dir.exists() or not (case_dir / "docs" / "architecture").exists():
        return None

    clean_legacy_directories(case_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_root = base_dir / ".archive"
    archive_target = archive_root / f"round_{timestamp}_{case_dir.name}"
    archive_root.mkdir(parents=True, exist_ok=True)

    shutil.copytree(case_dir, archive_target)
    print(f"📦 [自动归档] 既有产物已完整快照归档至: {archive_target}")
    return archive_target



def update_cases_index_readme(base_dir: Path) -> None:
    """在测试总目录生成/更新所有案例的索引文档."""
    case_entries = []
    for item in sorted(base_dir.iterdir()):
        if item.is_dir() and not item.name.startswith(".") and (item / "docs" / "architecture").exists():
            readme_path = item / "README.md"
            title = item.name
            if readme_path.exists():
                lines = readme_path.read_text(encoding="utf-8").splitlines()
                if lines:
                    title = lines[0].lstrip("#").strip() or item.name
            case_entries.append(f"- [{title}](./{item.name}/) - 路径: `{item.name}/`")

    index_content = f"""# 架构设计技能测试案例集 (Architecture Skill Test Cases)

本目录为 `architect_skill` 架构方法论与状态机驱动引擎的测试验证工作区。
每个案例均存放在独立的子目录中，拥有各自独立的全生命周期架构资产、交互画板与工程代码骨架。

## 已推演案例列表

{chr(10).join(case_entries) if case_entries else "*(暂无案例)*"}
"""
    (base_dir / "README.md").write_text(index_content, encoding="utf-8")
    print(f"📄 [索引更新] 测试总目录 README.md 已更新")


def main() -> None:
    parser = argparse.ArgumentParser(description="测试工作区通用归档与索引维护工具")
    parser.add_argument("action", choices=["archive", "index"], help="执行动作: archive (归档) 或 index (更新索引)")
    parser.add_argument("--case", help="指定要归档的案例目录名 (仅在 action=archive 时需要)")
    parser.add_argument(
        "--base-dir",
        default=os.path.expanduser("~/code/architect_skill_tests"),
        help="测试基准目录 (默认: ~/code/architect_skill_tests)"
    )
    args = parser.parse_args()
    base_dir = Path(args.base_dir).resolve()

    if args.action == "archive":
        if not args.case:
            print("❌ 错误: archive 动作必须通过 --case 指定案例名称")
            sys.exit(1)
        case_dir = base_dir / args.case
        archive_case_workspace(case_dir, base_dir)
    elif args.action == "index":
        update_cases_index_readme(base_dir)


if __name__ == "__main__":
    main()
