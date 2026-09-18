"""外部能力网关抽象端口 (Gateway Port)."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class GatewayPort(ABC):
    """外部 AI 推理/三方服务统一抽象网关."""

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """向外部服务或模型发起调用."""
        pass
