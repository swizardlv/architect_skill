"""自动化 Walking Skeleton 冒烟与端到端贯通测试."""

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
