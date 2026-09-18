"""领域核心实体与不变量 (Domain Models)."""

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
