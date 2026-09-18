"""业务流程编排服务 (Orchestration Service)."""

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
