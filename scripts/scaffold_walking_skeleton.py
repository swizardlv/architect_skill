"""Walking Skeleton 物理代码与冒烟测试自动化生成引擎.

(Scaffold Walking Skeleton Script for Architecture Execution Skill)
本脚本是 architecture-execution 技能的核心自动化工具，负责将纸面架构模型
（component-model, conceptual-data-model, boundary-contracts, walking-skeleton-spec）
真正转化为可直接运行、具备自动化测试验证的六边形工程物理骨架。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def find_architecture_dir(project_root: Path) -> Path:
    """定位架构文档根目录."""
    candidates = [
        project_root / "docs" / "architecture",
        project_root / "docs",
        project_root,
    ]
    for c in candidates:
        if (c / "02-models").exists() or (c / "04-delivery-and-organization").exists() or (c / "04-execution").exists():
            return c
    return project_root / "docs" / "architecture"


def extract_spec_data(arch_dir: Path) -> Dict[str, Any]:
    """从架构文档或规范文件中提取生成骨架所需的数据."""
    # 1. 尝试读取显式声明的 walking-skeleton-spec.json
    spec_paths = [
        arch_dir / "04-delivery-and-organization" / "walking-skeleton-spec.json",
        arch_dir / "04-execution" / "walking-skeleton-spec.json",
        arch_dir / "walking-skeleton-spec.json",
    ]
    for sp in spec_paths:
        if sp.exists():
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass

    # 2. 若未显式定义，提供标准的六边形元数据基准
    return {
        "project_name": arch_dir.parent.parent.name or "architecture_app",
        "architecture_style": "hexagonal",
        "directories": [
            "src/domain",
            "src/ports",
            "src/adapters",
            "src/services",
            "tests",
        ],
        "domain_entities": [
            {
                "name": "CoreTask",
                "fields": {"task_id": "str", "status": "str", "created_at": "datetime"},
            }
        ],
        "ports": ["StoragePort", "ExternalGatewayPort"],
        "adapters": ["InMemoryStorageAdapter", "MockExternalGatewayAdapter"],
        "services": ["OrchestrationService"],
    }


def generate_walking_skeleton(
    target_project_dir: Path,
    spec: Optional[Dict[str, Any]] = None,
    overwrite: bool = False,
) -> List[Path]:
    """根据架构契约与规范，在目标工程根目录下生成标准的物理骨架与测试."""
    target_project_dir = target_project_dir.resolve()
    arch_dir = find_architecture_dir(target_project_dir)
    if spec is None:
        spec = extract_spec_data(arch_dir)

    created_files: List[Path] = []

    # 1. 创建基础目录结构
    dirs = [
        target_project_dir / "src" / "domain",
        target_project_dir / "src" / "ports",
        target_project_dir / "src" / "adapters",
        target_project_dir / "src" / "services",
        target_project_dir / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    def write_if_not_exists(p: Path, content: str) -> None:
        if not p.exists() or overwrite:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content.strip() + "\n", encoding="utf-8")
            created_files.append(p)

    # 2. 生成 src/__init__.py 与子包 __init__.py
    write_if_not_exists(target_project_dir / "src" / "__init__.py", '"""Source root."""')
    write_if_not_exists(
        target_project_dir / "src" / "domain" / "__init__.py",
        '"""Domain package exports."""\nfrom .models import CoreTask, TaskStatus\n\n__all__ = ["CoreTask", "TaskStatus"]\n',
    )
    write_if_not_exists(
        target_project_dir / "src" / "ports" / "__init__.py",
        '"""Ports package exports."""\nfrom .storage import StoragePort\nfrom .gateway import GatewayPort\n\n__all__ = ["StoragePort", "GatewayPort"]\n',
    )
    write_if_not_exists(
        target_project_dir / "src" / "adapters" / "__init__.py",
        '"""Adapters package exports."""\nfrom .memory_storage import InMemoryStorageAdapter\nfrom .mock_gateway import MockGatewayAdapter\n\n__all__ = ["InMemoryStorageAdapter", "MockGatewayAdapter"]\n',
    )
    write_if_not_exists(
        target_project_dir / "src" / "services" / "__init__.py",
        '"""Services package exports."""\nfrom .orchestrator import CoreOrchestratorService\n\n__all__ = ["CoreOrchestratorService"]\n',
    )
    write_if_not_exists(target_project_dir / "tests" / "__init__.py", '"""Tests package."""')

    # 3. 生成 Domain 实体模型 (src/domain/models.py)
    domain_code = '''"""领域核心实体与不变量 (Domain Models)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional


class TaskStatus(str, Enum):
    """任务生命周期单向状态."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class CoreTask:
    """业务核心任务聚合根."""
    task_id: str
    tenant_id: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result_data: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, tenant_id: str, payload: Dict[str, Any]) -> CoreTask:
        return cls(
            task_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            payload=payload,
            status=TaskStatus.PENDING,
        )

    def mark_processing(self) -> None:
        self.status = TaskStatus.PROCESSING

    def mark_completed(self, result: Dict[str, Any]) -> None:
        self.status = TaskStatus.COMPLETED
        self.result_data = result

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.result_data = {"error": error}
'''
    write_if_not_exists(target_project_dir / "src" / "domain" / "models.py", domain_code)

    # 4. 生成 Ports 抽象端口 (src/ports/storage.py, src/ports/gateway.py)
    storage_port_code = '''"""存储抽象端口 (Storage Port)."""

from abc import ABC, abstractmethod
from typing import Optional
from ..domain.models import CoreTask


class StoragePort(ABC):
    """数据持久化抽象端口."""

    @abstractmethod
    def save(self, task: CoreTask) -> None:
        """保存任务状态."""
        pass

    @abstractmethod
    def find_by_id(self, task_id: str) -> Optional[CoreTask]:
        """根据任务 ID 查询任务."""
        pass
'''
    write_if_not_exists(target_project_dir / "src" / "ports" / "storage.py", storage_port_code)

    gateway_port_code = '''"""外部能力网关抽象端口 (Gateway Port)."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class GatewayPort(ABC):
    """外部 AI 推理/三方服务统一抽象网关."""

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """向外部服务或模型发起调用."""
        pass
'''
    write_if_not_exists(target_project_dir / "src" / "ports" / "gateway.py", gateway_port_code)

    # 5. 生成 Adapters 适配器实现 (src/adapters/memory_storage.py, src/adapters/mock_gateway.py)
    memory_storage_code = '''"""内存存储适配器实现 (In-Memory Storage Adapter)."""

from typing import Dict, Optional
from ..domain.models import CoreTask
from ..ports.storage import StoragePort


class InMemoryStorageAdapter(StoragePort):
    """内存字典存储实现，用于验证骨架与单元测试."""

    def __init__(self) -> None:
        self._store: Dict[str, CoreTask] = {}

    def save(self, task: CoreTask) -> None:
        self._store[task.task_id] = task

    def find_by_id(self, task_id: str) -> Optional[CoreTask]:
        return self._store.get(task_id)
'''
    write_if_not_exists(target_project_dir / "src" / "adapters" / "memory_storage.py", memory_storage_code)

    mock_gateway_code = '''"""外部网关 Mock 适配器 (Mock Gateway Adapter)."""

from typing import Dict, Any
from ..ports.gateway import GatewayPort


class MockGatewayAdapter(GatewayPort):
    """外部能力模拟适配器，用于离线冒烟与断言验证."""

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "processed_payload": payload,
            "tokens_or_quota": 100,
            "mocked": True,
        }
'''
    write_if_not_exists(target_project_dir / "src" / "adapters" / "mock_gateway.py", mock_gateway_code)

    # 6. 生成 Services 编排服务 (src/services/orchestrator.py)
    orchestrator_code = '''"""业务流程编排服务 (Orchestration Service)."""

from typing import Dict, Any, Optional
from ..domain.models import CoreTask, TaskStatus
from ..ports.storage import StoragePort
from ..ports.gateway import GatewayPort


class CoreOrchestratorService:
    """端到端核心业务调度服务."""

    def __init__(self, storage: StoragePort, gateway: GatewayPort) -> None:
        self.storage = storage
        self.gateway = gateway

    def submit_and_execute(self, tenant_id: str, payload: Dict[str, Any]) -> CoreTask:
        task = CoreTask.create(tenant_id=tenant_id, payload=payload)
        task.mark_processing()
        self.storage.save(task)

        try:
            res = self.gateway.execute(task.payload)
            task.mark_completed(result=res)
        except Exception as e:
            task.mark_failed(error=str(e))

        self.storage.save(task)
        return task

    def get_task_status(self, task_id: str) -> Optional[CoreTask]:
        return self.storage.find_by_id(task_id)
'''
    write_if_not_exists(target_project_dir / "src" / "services" / "orchestrator.py", orchestrator_code)

    # 7. 生成自动化测试 (tests/test_walking_skeleton.py)
    test_code = '''"""自动化 Walking Skeleton 冒烟与端到端贯通测试."""

import pytest
from src.domain.models import CoreTask, TaskStatus
from src.adapters.memory_storage import InMemoryStorageAdapter
from src.adapters.mock_gateway import MockGatewayAdapter
from src.services.orchestrator import CoreOrchestratorService


def test_walking_skeleton_smoke_flow():
    # 依赖注入六边形组件
    storage = InMemoryStorageAdapter()
    gateway = MockGatewayAdapter()
    service = CoreOrchestratorService(storage=storage, gateway=gateway)

    # 执行端到端闭环调用
    payload = {"input_content": "architect_smoke_test_data"}
    task = service.submit_and_execute(tenant_id="tenant-demo", payload=payload)

    # 验证状态与存储连通性
    assert task.status == TaskStatus.COMPLETED
    assert task.result_data is not None
    assert task.result_data.get("mocked") is True

    # 验证持久化层可精确查询
    persisted = service.get_task_status(task.task_id)
    assert persisted is not None
    assert persisted.task_id == task.task_id
    assert persisted.status == TaskStatus.COMPLETED
'''
    write_if_not_exists(target_project_dir / "tests" / "test_walking_skeleton.py", test_code)

    return created_files


def run_tests(project_root: Path) -> Tuple[bool, str]:
    """在目标工程下自动运行 pytest 检查."""
    cmd = [sys.executable, "-m", "pytest", str(project_root / "tests"), "-v"]
    try:
        res = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, timeout=30)
        output = res.stdout + "\n" + res.stderr
        return res.returncode == 0, output
    except Exception as e:
        return False, str(e)


def main() -> None:
    parser = argparse.ArgumentParser(description="自动为项目生成 Walking Skeleton 六边形代码骨架与测试")
    parser.add_argument("workspace_root", type=str, help="目标工程工作区根路径")
    parser.add_argument("--overwrite", action="store_true", help="是否强制覆盖现有代码")
    parser.add_argument("--run-test", action="store_true", help="生成后自动运行 pytest 验证")

    args = parser.parse_args()
    ws_root = Path(args.workspace_root).resolve()

    if not ws_root.exists():
        print(f"❌ 目标目录不存在: {ws_root}", file=sys.stderr)
        sys.exit(1)

    print(f"🏗️ [Walking Skeleton 脚手架] 开始为 {ws_root.name} 生成可执行骨架...")
    created = generate_walking_skeleton(ws_root, overwrite=args.overwrite)
    print(f"✅ 已生成/更新 {len(created)} 个骨架文件:")
    for f in created:
        print(f"   - {f.relative_to(ws_root)}")

    if args.run_test:
        print(f"🧪 [测试验证] 正在执行自动化测试...")
        passed, out = run_tests(ws_root)
        print(out)
        if not passed:
            print(f"❌ Walking Skeleton 测试未通过！", file=sys.stderr)
            sys.exit(1)
        print(f"🎉 Walking Skeleton 测试绿灯通过！")


if __name__ == "__main__":
    main()
