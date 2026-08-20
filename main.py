"""Thin AstrBot entry point for the Starpath Archive native tool."""

from __future__ import annotations

from astrbot.api import AstrBotConfig, llm_tool
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register

from .adapter import StarpathToolAdapter
from .core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from .core.repository import load_quotes, load_stars, load_tarot_cards


def build_service() -> StarpathService:
    """Assemble pure core services from static package data."""
    return StarpathService(
        StarEngine(load_stars()),
        TarotEngine(load_tarot_cards()),
        QuoteEngine(load_quotes()),
    )


@register(
    "starpath_plugin",
    "AstrBot Project",
    "Entertainment-focused symbolic celestial and tarot archive for Native Agent use.",
    "0.3.1-alpha",
    "",
)
class StarpathArchivePlugin(Star):
    """Expose one structured record generator; the Native Agent owns the reply."""

    def __init__(self, context: Context, config: AstrBotConfig | dict | None = None) -> None:
        super().__init__(context)
        del config
        self._adapter = StarpathToolAdapter(build_service())

    @llm_tool(name="generate_starpath_record")
    async def generate_starpath_record(
        self,
        event: AstrMessageEvent,
        mode: str = "daily",
        spread: str = "single",
    ) -> str:
        """Generate one symbolic entertainment record as JSON for Native Agent synthesis.

        Args:
            mode(string): Must be `daily`; determines the stable daily star.
            spread(string): Must be `single`; selects a single tarot card.

        Returns:
            JSON with star, tarot, and quote data. It contains cultural symbolism,
            not predictions, facts about a person's future, or life advice.
        """
        return await self._adapter.generate(event, mode, spread)
