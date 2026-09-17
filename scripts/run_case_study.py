"""多案例架构设计生命周期推演总调度器.

支持指定案例或一次性执行全部案例，隔离生成全生命周期架构资产、画板与工程代码骨架。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# 注册搜索路径
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skills" / "00_orchestrator"))

from scripts.cases.cbs_engine import run_cbs_case_study
from scripts.cases.robomesh_dispatcher import run_robomesh_case_study

CASES = {
    "cbs_engine": {
        "name": "cbs_engine",
        "title": "CBS-Engine: 跨境金融清算与反洗钱推理系统",
        "runner": run_cbs_case_study,
    },
    "robomesh_dispatcher": {
        "name": "robomesh_dispatcher",
        "title": "RoboMesh: 工业级多机自主移动机器人(AMR)无人仓协同调度中枢",
        "runner": run_robomesh_case_study,
    },
}


def update_cases_index_readme(base_dir: Path) -> None:
    """在测试总目录生成/更新所有案例的索引文档."""
    case_entries = []
    for item in sorted(base_dir.iterdir()):
        if item.is_dir() and (item / "docs" / "architecture").exists():
            readme_path = item / "README.md"
            title = item.name
            if readme_path.exists():
                first_line = readme_path.read_text(encoding="utf-8").splitlines()[0]
                title = first_line.lstrip("#").strip() or item.name
            case_entries.append(f"- [{title}](./{item.name}/) - 路径: `{item.name}/`")

    index_content = f"""# 架构设计技能测试案例集 (Architecture Skill Test Cases)

本目录为 `architect_skill` 架构方法论与状态机驱动引擎的测试验证工作区。
每个案例均存放在独立的子目录中，拥有各自独立的全生命周期架构资产、交互画板与工程代码骨架。

## 已推演案例列表

{chr(10).join(case_entries) if case_entries else "*(暂无案例)*"}

## 运行与扩展新案例

运行指定案例：
```bash
python scripts/run_case_study.py <case_name>
```
例如：
```bash
# 执行跨境清算案例
python scripts/run_case_study.py cbs_engine

# 执行无人仓机器人调度案例
python scripts/run_case_study.py robomesh_dispatcher

# 批量执行全部案例
python scripts/run_case_study.py all
```
"""
    (base_dir / "README.md").write_text(index_content, encoding="utf-8")
    print(f"\n -> 案例集索引总览已刷新: {base_dir / 'README.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="架构设计技能多案例推演驱动器")
    parser.add_argument(
        "case",
        nargs="?",
        default="all",
        help=f"要执行推演的案例名称 (支持: {', '.join(CASES.keys())}, all，默认: all)"
    )
    parser.add_argument(
        "--base-dir",
        default=os.path.expanduser("~/code/arhitect_skill_tests"),
        help="测试基准目录 (默认: ~/code/arhitect_skill_tests)"
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    cases_to_run = []
    if args.case == "all":
        cases_to_run = list(CASES.keys())
    elif args.case in CASES:
        cases_to_run = [args.case]
    else:
        print(f"⚠️ 未知案例名称: {args.case}，支持的值: {list(CASES.keys()) + ['all']}")
        sys.exit(1)

    for case_name in cases_to_run:
        case_info = CASES[case_name]
        case_dir = base_dir / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        case_info["runner"](case_dir)

    update_cases_index_readme(base_dir)


if __name__ == "__main__":
    main()
