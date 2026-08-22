"""Pure conversion from a Starpath domain record to Tarot experience input."""

from __future__ import annotations

from ..models import StarpathRecord
from .tarot import (
    ExperienceInputError,
    FortuneContext,
    TarotCardSelection,
    TarotExperienceInput,
)


class InvalidStarpathRecordError(ExperienceInputError):
    """Raised when a value is not a usable Starpath domain record."""


class MissingTarotCardError(ExperienceInputError):
    """Raised when a record cannot provide a stable logical Tarot card identity."""


class MissingDeckContextError(ExperienceInputError):
    """Raised when the caller does not explicitly choose a visual deck."""


class StarpathRecordExperienceAdapter:
    """Map existing domain data without drawing cards, resolving assets, or sending messages."""

    def adapt(
        self,
        record: StarpathRecord,
        *,
        deck_id: str,
        spread: str = "single",
    ) -> TarotExperienceInput:
        """Return a single-card experience input from one existing domain record."""
        self._validate_record(record)
        self._validate_deck_context(deck_id)
        card_id = record.tarot.card.id
        if not isinstance(card_id, str) or not card_id:
            raise MissingTarotCardError("Starpath record is missing tarot.card.id")

        return TarotExperienceInput(
            deck_id=deck_id,
            spread=spread,
            cards=(TarotCardSelection(card_id=card_id, position="main"),),
            fortune_context=FortuneContext(
                quote_id=record.quote.id,
                text=record.quote.text,
                theme=record.quote.theme,
            ),
        )

    @staticmethod
    def _validate_record(record: StarpathRecord) -> None:
        if not isinstance(record, StarpathRecord):
            raise InvalidStarpathRecordError("Expected a StarpathRecord domain value")

    @staticmethod
    def _validate_deck_context(deck_id: str) -> None:
        if not isinstance(deck_id, str) or not deck_id:
            raise MissingDeckContextError("A caller-selected deck_id is required")
