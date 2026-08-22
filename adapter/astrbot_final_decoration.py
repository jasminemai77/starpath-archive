"""AstrBot-only final response decoration for an already captured presentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ..experience.delivery import LocalRuntimeImageDelivery
from ..experience.presentation_consumer import (
    PresentationConsumer,
    ResourceElement,
)
from .astrbot_native_image import build_native_image_component
from .astrbot_platform import AstrBotAdapter

PRESENTATION_EXTRA_KEY = "starpath.experience.presentation"
PRESENTATION_CONSUMED_EXTRA_KEY = "starpath.experience.presentation_consumed"
DECORATION_STATUS_EXTRA_KEY = "starpath.experience.decoration_status"


class FinalDecorationError(ValueError):
    """Raised for a presentation that cannot provide one final image component."""


class AstrBotFinalDecoration:
    """Append one AstrBot image to the existing non-streaming Agent result.

    This boundary neither creates a result nor delivers it.  AstrBot's normal
    response stage remains solely responsible for sending the existing chain.
    """

    def __init__(
        self,
        presentation_consumer: PresentationConsumer,
        astrbot_adapter: AstrBotAdapter,
        tarot_asset_root: str | Path,
        image_component_builder: Callable[[object], object] = build_native_image_component,
    ) -> None:
        self._presentation_consumer = presentation_consumer
        self._astrbot_adapter = astrbot_adapter
        self._tarot_asset_root = Path(tarot_asset_root)
        self._image_component_builder = image_component_builder

    def decorate(self, event: Any) -> None:
        """Append one image when capture data and a non-streaming result are present."""
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
            platform_presentation = self._presentation_consumer.consume(presentation)
            resource = self._single_image_resource(platform_presentation.elements)
            payload = self._astrbot_adapter.build_image_payload(resource)
            deck_id = payload.metadata.get("deck_id")
            if not isinstance(deck_id, str) or not deck_id:
                raise FinalDecorationError("Image resource requires a deck_id")
            prepared = LocalRuntimeImageDelivery(self._tarot_asset_root / deck_id).prepare(
                payload
            )
            result.chain.append(self._image_component_builder(prepared))
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

    @staticmethod
    def _single_image_resource(elements: tuple[object, ...]):
        resources = [
            element.resource
            for element in elements
            if isinstance(element, ResourceElement)
        ]
        if len(resources) != 1:
            raise FinalDecorationError("Final decoration requires exactly one image resource")
        return resources[0]
