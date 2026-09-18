"""内存存储适配器实现 (In-Memory Storage Adapter)."""

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
