import os
import shutil
import sys
import tempfile
from pathlib import Path
import pytest

TEST_DIR = Path(__file__).parent.resolve()
REPO_ROOT = TEST_DIR.parent.resolve()
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from scaffold_walking_skeleton import generate_walking_skeleton, run_tests



@pytest.fixture
def temp_project_dir():
    temp_dir = tempfile.mkdtemp(prefix="test_walking_skeleton_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_generate_and_run_walking_skeleton(temp_project_dir: Path):
    # 1. 模拟一个最小架构目录
    arch_dir = temp_project_dir / "docs" / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)

    # 2. 执行脚手架生成
    created_files = generate_walking_skeleton(temp_project_dir, overwrite=True)
    assert len(created_files) > 0

    # 3. 验证关键六边形目录与源码已生成
    assert (temp_project_dir / "src" / "domain" / "models.py").exists()
    assert (temp_project_dir / "src" / "ports" / "storage.py").exists()
    assert (temp_project_dir / "src" / "ports" / "gateway.py").exists()
    assert (temp_project_dir / "src" / "adapters" / "memory_storage.py").exists()
    assert (temp_project_dir / "src" / "adapters" / "mock_gateway.py").exists()
    assert (temp_project_dir / "src" / "services" / "orchestrator.py").exists()
    assert (temp_project_dir / "tests" / "test_walking_skeleton.py").exists()

    # 4. 执行自动测试验证
    passed, output = run_tests(temp_project_dir)
    assert passed, f"Generated test failed: {output}"
    assert "PASSED" in output
