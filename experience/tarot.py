"""Platform-neutral orchestration for one resolved Tarot experience."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.resolver import AssetResolver
from .asset_consumer import AssetReferenceConsumer, DisplayResource


class ExperienceInputError(ValueError):
    """Raised when an experience request cannot describe the MVP single-card flow."""


class ExperienceBuildError(RuntimeError):
    """Reserved for a future failure while assembling non-resolver experience data."""


@dataclass(frozen=True)
class TarotCardSelection:
    """One logical card selected by a domain reading, with a semantic position."""

    card_id: str
    position: str

    def __post_init__(self) -> None:
        if not isinstance(self.card_id, str) or not self.card_id:
            raise ExperienceInputError("A Tarot card selection requires a card_id")
        if not isinstance(self.position, str) or not self.position:
            raise ExperienceInputError("A Tarot card selection requires a position")


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
    spread: str
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
                content=f"{selection.position}: {selection.card_id}",
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
