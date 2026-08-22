"""AstrBot-only final response decoration for an already captured presentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..experience.message_presentation import PresentationResultMessageConverter
from .astrbot_forward_runtime import AstrBotForwardRuntimeAdapter
from .qq_forward import QQForwardMessageAdapter

PRESENTATION_EXTRA_KEY = "starpath.experience.presentation"
PRESENTATION_CONSUMED_EXTRA_KEY = "starpath.experience.presentation_consumed"
DECORATION_STATUS_EXTRA_KEY = "starpath.experience.decoration_status"


class AstrBotFinalDecoration:
    """Append one AstrBot ``Nodes`` component to a non-streaming Agent result.

    This boundary neither creates a result nor delivers it.  AstrBot's normal
    response stage remains solely responsible for sending the existing chain.
    """

    def __init__(
        self,
        tarot_asset_root: str | Path,
        forward_runtime: AstrBotForwardRuntimeAdapter | None = None,
        message_converter: PresentationResultMessageConverter | None = None,
        forward_adapter: QQForwardMessageAdapter | None = None,
    ) -> None:
        self._forward_runtime = forward_runtime or AstrBotForwardRuntimeAdapter(tarot_asset_root)
        self._message_converter = message_converter or PresentationResultMessageConverter()
        self._forward_adapter = forward_adapter or QQForwardMessageAdapter()

    def decorate(self, event: Any) -> None:
        """Append one forward message when capture data and a normal result are present."""
        if event.get_extra(PRESENTATION_CONSUMED_EXTRA_KEY, False):
            return

        presentation = event.get_extra(PRESENTATION_EXTRA_KEY)
        if presentation is None:
            return

        result = event.get_result()
        if result is None or not getattr(result, "chain", None):
            return
        if self._is_streaming(result):
            event.set_extra(DECORATION_STATUS_EXTRA_KEY, "skipped_streaming")
            return

        try:
            message = self._message_converter.convert(presentation)
            forward_payload = self._forward_adapter.adapt(message)
            result.chain.append(self._forward_runtime.build_nodes(event, forward_payload))
            event.set_extra(PRESENTATION_CONSUMED_EXTRA_KEY, True)
            event.set_extra(DECORATION_STATUS_EXTRA_KEY, "attached")
        except Exception:
            event.set_extra(DECORATION_STATUS_EXTRA_KEY, "failed")

    @staticmethod
    def _is_streaming(result: object) -> bool:
        content_type = getattr(result, "result_content_type", None)
        return getattr(content_type, "name", None) in {
            "STREAMING_RESULT",
            "STREAMING_FINISH",
        }
