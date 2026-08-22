"""Pure producer for future ``starpath.tool.v2`` JSON results.

This builder is intentionally not an AstrBot Tool and is not registered by the
plugin.  A later integration can supply its own draw policy without changing
the stable v1 producer.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from ..contracts.starpath_tool_v2 import (
    FUTURE_STARPATH_TOOL_V2,
    FutureStarpathToolContractError,
    FutureStarpathToolV2Parser,
)
from ..models import Quote, Star, TarotDraw


class V2ToolProducerError(ValueError):
    """Raised when a caller cannot build a valid v2 symbolic result."""


class TarotDrawProvider(Protocol):
    """Supply one selected Tarot draw without imposing a selection policy."""

    def draw(self) -> TarotDraw:
        """Return one complete non-predictive Tarot draw."""


class StarpathToolV2Producer:
    """Build validated v2 result dictionaries for supported logical spreads."""

    _POSITIONS_BY_SPREAD = {
        "single": ("main",),
        "three_card": ("past", "present", "future"),
    }

    def __init__(
        self,
        draw_provider: TarotDrawProvider,
        *,
        now: Callable[[], datetime] | None = None,
        record_id_factory: Callable[[], str] | None = None,
        validator: FutureStarpathToolV2Parser | None = None,
    ) -> None:
        self._draw_provider = draw_provider
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._record_id_factory = record_id_factory or self._default_record_id
        self._validator = validator or FutureStarpathToolV2Parser()

    def build(
        self,
        *,
        star: Star,
        quote: Quote,
        spread: str,
        mode: str = "daily",
    ) -> dict[str, object]:
        """Build and validate an independent v2 result without delivery work."""
        if mode != "daily":
            raise V2ToolProducerError("mode must be 'daily'")
        positions = self._POSITIONS_BY_SPREAD.get(spread)
        if positions is None:
            raise V2ToolProducerError("spread must be 'single' or 'three_card'")
        if not isinstance(star, Star):
            raise V2ToolProducerError("star must be a Star domain value")
        if not isinstance(quote, Quote):
            raise V2ToolProducerError("quote must be a Quote domain value")

        draws = tuple(self._draw() for _ in positions)
        generated_at = self._now().astimezone(timezone.utc)
        payload: dict[str, object] = {
            "record_id": self._record_id(),
            "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
            "mode": mode,
            "star": asdict(star),
            "tarot": {
                "spread": spread,
                "cards": [
                    self._card_payload(draw, position, order)
                    for order, (draw, position) in enumerate(zip(draws, positions, strict=True))
                ],
            },
            "quote": asdict(quote),
            "metadata": {
                "contract_version": FUTURE_STARPATH_TOOL_V2,
                "content_scope": "symbolic_entertainment",
                "generation_timezone": "UTC",
                "experience": {
                    "star_type": star.type,
                    "tarot_arcanas": [draw.card.arcana for draw in draws],
                    "tarot_orientations": [draw.orientation for draw in draws],
                    "quote_theme": quote.theme,
                },
            },
        }
        try:
            self._validator.parse(payload)
        except FutureStarpathToolContractError as error:
            raise V2ToolProducerError(
                "Generated result does not satisfy starpath.tool.v2"
            ) from error
        return payload

    def _draw(self) -> TarotDraw:
        draw = self._draw_provider.draw()
        if not isinstance(draw, TarotDraw):
            raise V2ToolProducerError("draw provider must return a TarotDraw")
        return draw

    def _record_id(self) -> str:
        record_id = self._record_id_factory()
        if not isinstance(record_id, str) or not record_id.strip():
            raise V2ToolProducerError("record_id_factory must return a non-empty string")
        return record_id

    @staticmethod
    def _default_record_id() -> str:
        return f"starpath-{uuid4().hex}"

    @staticmethod
    def _card_payload(draw: TarotDraw, position: str, order: int) -> dict[str, object]:
        return {
            **draw.as_dict(),
            "position": position,
            "order": order,
        }
