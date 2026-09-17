"""针对多案例推演调度器的集成测试."""

import os
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from scripts.cases.cbs_engine import run_cbs_case_study
from scripts.cases.robomesh_dispatcher import run_robomesh_case_study
from scripts.run_case_study import update_cases_index_readme


def test_run_cbs_case_study_in_temp_dir(tmp_path: Path) -> None:
    case_dir = (tmp_path / "cbs_engine").resolve()
    case_dir.mkdir(parents=True, exist_ok=True)
    run_cbs_case_study(case_dir)

    assert (case_dir / "docs" / "architecture" / ".state.json").exists()
    assert (case_dir / "docs" / "architecture" / "architecture_board.html").exists()
    assert (case_dir / "src" / "domain" / "models.py").exists()
    assert (case_dir / "src" / "ports" / "settlement_port.py").exists()
    assert (case_dir / ".agent-rules.md").exists()
    assert (case_dir / "README.md").exists()


def test_run_robomesh_case_study_in_temp_dir(tmp_path: Path) -> None:
    case_dir = (tmp_path / "robomesh_dispatcher").resolve()
    case_dir.mkdir(parents=True, exist_ok=True)
    run_robomesh_case_study(case_dir)

    assert (case_dir / "docs" / "architecture" / ".state.json").exists()
    assert (case_dir / "docs" / "architecture" / "architecture_board.html").exists()
    assert (case_dir / "src" / "domain" / "models.py").exists()
    assert (case_dir / "src" / "ports" / "dispatcher_port.py").exists()
    assert (case_dir / "src" / "adapters" / "spatial_reservation.py").exists()
    assert (case_dir / ".agent-rules.md").exists()
    assert (case_dir / "README.md").exists()


def test_update_cases_index_readme(tmp_path: Path) -> None:
    base_dir = tmp_path / "cases"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    cbs_dir = base_dir / "cbs"
    cbs_dir.mkdir(parents=True, exist_ok=True)
    (cbs_dir / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
    (cbs_dir / "README.md").write_text("# Case 1: CBS", encoding="utf-8")

    update_cases_index_readme(base_dir)

    readme_content = (base_dir / "README.md").read_text(encoding="utf-8")
    assert "Case 1: CBS" in readme_content
