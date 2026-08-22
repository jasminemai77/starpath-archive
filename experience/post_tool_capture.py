"""Mock-only, post-tool capture of platform-neutral Starpath presentation state."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .application import TarotExperienceApplication
from .presentation import ExperiencePresentationBuilder

STARPATH_TOOL_NAME = "generate_starpath_record"
PRESENTATION_EXTRA_KEY = "starpath.experience.presentation"
CAPTURE_STATUS_EXTRA_KEY = "starpath.experience.capture_status"


class StarpathExperienceCaptureHook:
    """Capture one Starpath presentation after the matching Tool returns; never deliver it."""

    def __init__(
        self,
        extractor: Callable[[object], object],
        application: TarotExperienceApplication,
        presentation_builder: ExperiencePresentationBuilder,
        deck_id_provider: Callable[[dict | None], str],
    ) -> None:
        self._extractor = extractor
        self._application = application
        self._presentation_builder = presentation_builder
        self._deck_id_provider = deck_id_provider

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
            record = self._extractor(tool_result)
            spread = (tool_args or {}).get("spread", "single")
            experience = self._application.build(
                record, deck_id=self._deck_id_provider(tool_args), spread=spread
            )
            presentation = self._presentation_builder.build(experience, mode="quick")
            event.set_extra(PRESENTATION_EXTRA_KEY, presentation)
            event.set_extra(CAPTURE_STATUS_EXTRA_KEY, "captured")
        except Exception:
            event.set_extra(CAPTURE_STATUS_EXTRA_KEY, "failed")
