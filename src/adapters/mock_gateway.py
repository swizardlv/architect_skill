"""外部网关 Mock 适配器 (Mock Gateway Adapter)."""

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
