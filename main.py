"""Thin AstrBot entry point for the Starpath Archive native tool."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from astrbot.api import AstrBotConfig, llm_tool
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .adapter import StarpathToolAdapter
from .adapter.astrbot_final_decoration import AstrBotFinalDecoration
from .adapter.astrbot_platform import AstrBotAdapter
from .core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from .core.manifest.providers import JSONManifestProvider
from .core.repository import load_quotes, load_stars, load_tarot_cards
from .core.resolver import DefaultAssetResolver
from .experience.application import TarotExperienceApplication
from .experience.asset_consumer import DefaultAssetReferenceConsumer
from .experience.deck_provider import PackageDeckProvider
from .experience.post_tool_capture import StarpathExperienceCaptureHook
from .experience.presentation import ExperiencePresentationBuilder
from .experience.presentation_consumer import StructuredPresentationConsumer
from .experience.record_adapter import StarpathRecordExperienceAdapter
from .experience.tarot import TarotExperienceOrchestrator
from .experience.tool_result_parser import StarpathToolResultParser, ToolResultExtractor


def build_service() -> StarpathService:
    """Assemble pure core services from static package data."""
    return StarpathService(
        StarEngine(load_stars()),
        TarotEngine(load_tarot_cards()),
        QuoteEngine(load_quotes()),
    )


def build_experience_application() -> TarotExperienceApplication:
    """Assemble capture-only experience dependencies from packaged manifests."""
    manifest_root = Path(__file__).parent / "assets" / "tarot"
    resolver = DefaultAssetResolver(JSONManifestProvider(manifest_root))
    orchestrator = TarotExperienceOrchestrator(
        resolver,
        DefaultAssetReferenceConsumer(),
    )
    return TarotExperienceApplication(StarpathRecordExperienceAdapter(), orchestrator)


def build_final_decoration() -> AstrBotFinalDecoration:
    """Assemble the append-only AstrBot final decoration boundary."""
    return AstrBotFinalDecoration(
        StructuredPresentationConsumer(),
        AstrBotAdapter(),
        Path(__file__).parent / "assets" / "tarot",
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
        self._adapter = StarpathToolAdapter(build_service())
        config_mapping = config if isinstance(config, Mapping) else None
        self._capture_hook = StarpathExperienceCaptureHook.from_tool_result(
            ToolResultExtractor(),
            StarpathToolResultParser(),
            build_experience_application(),
            ExperiencePresentationBuilder(),
            PackageDeckProvider(Path(__file__).parent / "assets" / "tarot", config_mapping),
        )
        self._final_decoration = build_final_decoration()

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

    @filter.on_llm_tool_respond()
    async def capture_starpath_tool_result(
        self,
        event: AstrMessageEvent,
        tool: object,
        tool_args: dict | None,
        tool_result: object,
    ) -> None:
        """Capture a resolved presentation in event extras; never alter delivery."""
        await self._capture_hook.capture(event, tool, tool_args, tool_result)

    @filter.on_decorating_result()
    async def decorate_starpath_final_result(self, event: AstrMessageEvent) -> None:
        """Append one captured Tarot image to the Native Agent's final response chain."""
        self._final_decoration.decorate(event)
