"""Application-level composition for the platform-neutral Tarot experience flow."""

from __future__ import annotations

from ..models import StarpathRecord
from .record_adapter import StarpathRecordExperienceAdapter
from .tarot import ExperienceResult, TarotExperienceInput, TarotExperienceOrchestrator


class TarotExperienceApplication:
    """Compose record adaptation and experience construction without adding behaviour."""

    def __init__(
        self,
        adapter: StarpathRecordExperienceAdapter,
        orchestrator: TarotExperienceOrchestrator,
    ) -> None:
        self._adapter = adapter
        self._orchestrator = orchestrator

    def build(
        self,
        record: StarpathRecord,
        *,
        deck_id: str,
        spread: str,
    ) -> ExperienceResult:
        """Build one experience by delegating to the injected adapter and orchestrator."""
        experience_input = self._adapter.adapt(
            record,
            deck_id=deck_id,
            spread=spread,
        )
        return self._orchestrator.build(experience_input)

    def build_input(self, experience_input: TarotExperienceInput) -> ExperienceResult:
        """Build already-adapted input, used by a future versioned Tool contract."""
        return self._orchestrator.build(experience_input)
