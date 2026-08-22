"""AstrBot runtime conversion for already-adapted QQ forward payloads."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ..experience.delivery import LocalRuntimeImageDelivery
from .astrbot_native_image import build_native_image_component
from .astrbot_platform import AstrBotAdapter
from .qq_forward import QQForwardPayload


class AstrBotForwardRuntimeError(ValueError):
    """Raised when a semantic QQ forward payload cannot become AstrBot Nodes."""


class AstrBotForwardRuntimeAdapter:
    """Convert semantic payload nodes to AstrBot ``Nodes`` without delivery calls."""

    def __init__(
        self,
        tarot_asset_root: str | Path,
        *,
        image_component_builder: Callable[[object], object] = build_native_image_component,
    ) -> None:
        self._tarot_asset_root = Path(tarot_asset_root)
        self._image_component_builder = image_component_builder
        self._astrbot_adapter = AstrBotAdapter()

    def build_nodes(self, event: Any, payload: QQForwardPayload) -> object:
        """Return one AstrBot ``Nodes`` component with ordered forward entries."""
        import astrbot.api.message_components as Comp

        sender_id = self._sender_id(event)
        nodes = []
        for payload_node in payload.nodes:
            if payload_node.node_type == "text":
                content = [Comp.Plain(payload_node.text)]
            elif payload_node.node_type == "resource":
                resource = payload_node.resource
                if resource is None:
                    raise AstrBotForwardRuntimeError("Forward resource node is missing data")
                image_payload = self._astrbot_adapter.build_image_payload(resource)
                deck_id = image_payload.metadata.get("deck_id")
                if not isinstance(deck_id, str) or not deck_id:
                    raise AstrBotForwardRuntimeError("Forward image requires a deck_id")
                prepared = LocalRuntimeImageDelivery(self._tarot_asset_root / deck_id).prepare(
                    image_payload
                )
                content = [self._image_component_builder(prepared)]
            else:
                raise AstrBotForwardRuntimeError("Unsupported forward payload node")
            nodes.append(Comp.Node(uin=sender_id, name=payload.title, content=content))
        return Comp.Nodes(nodes)

    @staticmethod
    def _sender_id(event: object) -> str:
        get_self_id = getattr(event, "get_self_id", None)
        value = get_self_id() if callable(get_self_id) else None
        if value is None or not str(value).strip():
            return "0"
        return str(value)
