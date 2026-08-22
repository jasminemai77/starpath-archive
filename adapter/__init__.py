"""AstrBot-specific boundary adapters."""

from .qq_forward import QQForwardMessageAdapter, QQForwardNode, QQForwardPayload
from .tool_adapter import StarpathToolAdapter
from .tool_v2_adapter import StarpathToolV2Adapter

__all__ = [
    "QQForwardMessageAdapter",
    "QQForwardNode",
    "QQForwardPayload",
    "StarpathToolAdapter",
    "StarpathToolV2Adapter",
    "AstrBotForwardRuntimeAdapter",
]
from .astrbot_forward_runtime import AstrBotForwardRuntimeAdapter
