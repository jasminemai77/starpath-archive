"""Platform-neutral orchestration for one resolved Tarot experience."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..core.resolver import AssetResolver
from .asset_consumer import AssetReferenceConsumer, DisplayResource


class ExperienceInputError(ValueError):
    """Raised when an experience request cannot describe the MVP single-card flow."""


class ExperienceBuildError(RuntimeError):
    """Reserved for a future failure while assembling non-resolver experience data."""


class SpreadType(str, Enum):
    """Named spread shapes supported by the current Tarot domain vocabulary."""

    SINGLE = "single"
    THREE_CARD = "three_card"


class CardPosition(str, Enum):
    """Semantic card positions for the currently defined spread shapes."""

    MAIN = "main"
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


@dataclass(frozen=True)
class TarotCardSelection:
    """One logical card selected by a domain reading, with a semantic position."""

    card_id: str
    position: CardPosition | str
    order: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.card_id, str) or not self.card_id:
            raise ExperienceInputError("A Tarot card selection requires a card_id")
        try:
            position = CardPosition(self.position)
        except (TypeError, ValueError) as error:
            raise ExperienceInputError(
                "A Tarot card selection requires a known position"
            ) from error
        if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order < 0:
            raise ExperienceInputError("A Tarot card selection requires a non-negative order")
        object.__setattr__(self, "position", position)


@dataclass(frozen=True)
class TarotSpread:
    """A validated ordered domain shape for a selected set of Tarot cards.

    It introduces single- and three-card semantics without changing the current
    ``TarotExperienceInput`` or activating multi-card runtime resolution.
    """

    spread_type: SpreadType | str
    cards: tuple[TarotCardSelection, ...]

    def __post_init__(self) -> None:
        try:
            spread_type = SpreadType(self.spread_type)
        except (TypeError, ValueError) as error:
            raise ExperienceInputError("A Tarot spread requires a known spread type") from error
        if not self.cards:
            raise ExperienceInputError("A Tarot spread requires at least one card")
        if not all(isinstance(card, TarotCardSelection) for card in self.cards):
            raise ExperienceInputError("A Tarot spread requires Tarot card selections")
        if len({card.order for card in self.cards}) != len(self.cards):
            raise ExperienceInputError("Tarot spread card orders must be unique")

        ordered_cards = tuple(sorted(self.cards, key=lambda card: card.order))
        self._validate_shape(spread_type, ordered_cards)
        object.__setattr__(self, "spread_type", spread_type)
        object.__setattr__(self, "cards", ordered_cards)

    @staticmethod
    def _validate_shape(
        spread_type: SpreadType,
        cards: tuple[TarotCardSelection, ...],
    ) -> None:
        expected_positions = {
            SpreadType.SINGLE: (CardPosition.MAIN,),
            SpreadType.THREE_CARD: (
                CardPosition.PAST,
                CardPosition.PRESENT,
                CardPosition.FUTURE,
            ),
        }[spread_type]
        if tuple(card.position for card in cards) != expected_positions:
            raise ExperienceInputError(
                f"{spread_type.value} spread requires positions "
                f"{[position.value for position in expected_positions]} in order"
            )


@dataclass(frozen=True)
class FortuneContext:
    """Existing cultural quote data, without predictive interpretation."""

    quote_id: str
    text: str
    theme: str


@dataclass(frozen=True)
class TarotExperienceInput:
    """Business input for visual experience composition; deck selection is explicit."""

    deck_id: str
    spread: SpreadType | str
    cards: tuple[TarotCardSelection, ...]
    fortune_context: FortuneContext | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.deck_id, str) or not self.deck_id:
            raise ExperienceInputError("Tarot experience requires an explicit deck_id")
        if not isinstance(self.spread, str) or not self.spread:
            raise ExperienceInputError("Tarot experience requires a spread")
        if not self.cards:
            raise ExperienceInputError("Tarot experience requires at least one card")


@dataclass(frozen=True)
class ExperienceTextSection:
    """A source-backed text fragment for a future platform or Agent consumer."""

    section_id: str
    title: str
    content: str


@dataclass(frozen=True)
class ExperienceResult:
    """Platform-neutral experience plan containing no sender or platform payload."""

    title: str
    spread: str
    cards: tuple[TarotCardSelection, ...]
    display_resources: tuple[DisplayResource, ...]
    text_sections: tuple[ExperienceTextSection, ...]
    fortune_context: FortuneContext | None


class TarotExperienceOrchestrator:
    """Resolve a domain-selected card into a display-ready, platform-neutral result."""

    def __init__(
        self,
        resolver: AssetResolver,
        consumer: AssetReferenceConsumer,
    ) -> None:
        self._resolver = resolver
        self._consumer = consumer

    def build(self, experience_input: TarotExperienceInput) -> ExperienceResult:
        """Build the MVP single-card experience without performing delivery work."""
        self._validate_single_card(experience_input)
        selection = experience_input.cards[0]
        reference = self._resolver.resolve(experience_input.deck_id, selection.card_id)
        resource = self._consumer.consume(reference)
        return ExperienceResult(
            title="Tarot experience",
            spread=experience_input.spread,
            cards=experience_input.cards,
            display_resources=(resource,),
            text_sections=self._text_sections(experience_input),
            fortune_context=experience_input.fortune_context,
        )

    @staticmethod
    def _validate_single_card(experience_input: TarotExperienceInput) -> None:
        if experience_input.spread != "single" or len(experience_input.cards) != 1:
            raise ExperienceInputError(
                "The Tarot experience MVP currently supports exactly one single-spread card"
            )

    @staticmethod
    def _text_sections(
        experience_input: TarotExperienceInput,
    ) -> tuple[ExperienceTextSection, ...]:
        selection = experience_input.cards[0]
        sections = [
            ExperienceTextSection(
                section_id="tarot",
                title="Tarot",
                content=f"{selection.position.value}: {selection.card_id}",
            )
        ]
        if experience_input.fortune_context is not None:
            sections.append(
                ExperienceTextSection(
                    section_id="fortune_sign",
                    title="Fortune sign",
                    content=experience_input.fortune_context.text,
                )
            )
        return tuple(sections)
