"""Post-tool capture of platform-neutral Starpath presentation state only."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .application import TarotExperienceApplication
from .deck_provider import DeckProvider
from .presentation import ExperiencePresentationBuilder
from .tool_contract_dispatcher import (
    StarpathToolContractDispatcher,
    V2TarotExperiencePayload,
)
from .tool_result_parser import StarpathToolResultParser, ToolResultExtractor

STARPATH_TOOL_NAME = "generate_starpath_record"
PRESENTATION_EXTRA_KEY = "starpath.experience.presentation"
CAPTURE_STATUS_EXTRA_KEY = "starpath.experience.capture_status"


class StarpathExperienceCaptureHook:
    """Capture one Starpath presentation after the matching Tool returns; never deliver it."""

    def __init__(
        self,
        record_extractor: Callable[[object], object],
        application: TarotExperienceApplication,
        presentation_builder: ExperiencePresentationBuilder,
        deck_provider: DeckProvider,
    ) -> None:
        self._record_extractor = record_extractor
        self._application = application
        self._presentation_builder = presentation_builder
        self._deck_provider = deck_provider

    @classmethod
    def from_tool_result(
        cls,
        tool_result_extractor: ToolResultExtractor,
        parser: StarpathToolResultParser,
        application: TarotExperienceApplication,
        presentation_builder: ExperiencePresentationBuilder,
        deck_provider: DeckProvider,
        dispatcher: StarpathToolContractDispatcher | None = None,
    ) -> "StarpathExperienceCaptureHook":
        """Compose the production extraction and parser boundary at registration time."""

        contract_dispatcher = dispatcher or StarpathToolContractDispatcher(parser)

        def extract_record(tool_result: object) -> object:
            return contract_dispatcher.parse(tool_result_extractor.extract(tool_result))

        return cls(
            extract_record,
            application,
            presentation_builder,
            deck_provider,
        )

    async def capture(
        self, event: Any, tool: Any, tool_args: dict | None, tool_result: object
    ) -> None:
        """Save one immutable presentation state, silently degrading on capture failure."""
        if getattr(tool, "name", None) != STARPATH_TOOL_NAME:
            return
        if event.get_extra(CAPTURE_STATUS_EXTRA_KEY) in {"captured", "failed"}:
            return
        event.set_extra(CAPTURE_STATUS_EXTRA_KEY, "pending")
        try:
            parsed_result = self._record_extractor(tool_result)
            deck_id = self._deck_provider.get_default_deck_id()
            if isinstance(parsed_result, V2TarotExperiencePayload):
                experience = self._application.build_input(
                    parsed_result.to_experience_input(deck_id)
                )
            else:
                spread = (tool_args or {}).get("spread", "single")
                experience = self._application.build(
                    parsed_result,
                    deck_id=deck_id,
                    spread=spread,
                )
            presentation = self._presentation_builder.build(experience, mode="quick")
            event.set_extra(PRESENTATION_EXTRA_KEY, presentation)
            event.set_extra(CAPTURE_STATUS_EXTRA_KEY, "captured")
        except Exception:
            event.set_extra(CAPTURE_STATUS_EXTRA_KEY, "failed")
