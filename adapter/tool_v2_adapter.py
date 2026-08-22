"""Expose the pure v2 builder through a future Native Tool boundary only."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from ..core import (
    QuoteEngine,
    StarEngine,
    StarpathToolV2Producer,
    V2ToolProducerError,
    ValidationError,
)
from .tool_adapter import StarpathToolAdapter


class StarpathToolV2Adapter:
    """Build v2 JSON without inspecting message text, delivery, or Agent state."""

    def __init__(
        self,
        star_engine: StarEngine,
        quote_engine: QuoteEngine,
        producer: StarpathToolV2Producer,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._star_engine = star_engine
        self._quote_engine = quote_engine
        self._producer = producer
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def generate(self, event: Any, mode: str = "daily", spread: str = "single") -> str:
        """Return a v2 symbolic result for an Agent-selected supported spread."""
        try:
            generated_at = self._now().astimezone(timezone.utc)
            star = self._star_engine.select_daily_star(
                StarpathToolAdapter._event_user_hash(event), generated_at.date()
            )
            payload = self._producer.build(
                star=star,
                quote=self._quote_engine.draw(),
                spread=spread,
                mode=mode,
                generated_at=generated_at,
            )
        except (ValidationError, V2ToolProducerError) as error:
            return json.dumps(
                {"error": "INVALID_PARAMETERS", "reason": str(error)}, ensure_ascii=False
            )
        return json.dumps(payload, ensure_ascii=False)
