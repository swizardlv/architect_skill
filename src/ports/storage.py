"""存储抽象端口 (Storage Port)."""

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
