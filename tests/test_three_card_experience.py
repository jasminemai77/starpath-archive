"""Tests for the platform-neutral three-card Tarot experience flow."""

from __future__ import annotations

import pytest
from starpath_plugin.core.resolver import AssetNotFoundError, AssetReference, AssetResolver
from starpath_plugin.experience.asset_consumer import DefaultAssetReferenceConsumer
from starpath_plugin.experience.message_presentation import PresentationResultMessageConverter
from starpath_plugin.experience.presentation import (
    ExperiencePresentationBuilder,
    ImagePresentation,
    TextPresentation,
)
from starpath_plugin.experience.tarot import (
    ExperienceInputError,
    TarotCardSelection,
    TarotExperienceInput,
    TarotExperienceOrchestrator,
)


class RecordingResolver(AssetResolver):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        self.calls.append((deck_id, card_id))
        if card_id == "missing_card":
            raise AssetNotFoundError(deck_id, card_id)
        return AssetReference(
            deck_id=deck_id,
            card_id=card_id,
            asset_key=f"{deck_id}_{card_id}",
            path=f"major/{card_id}.png",
            format="png",
            version="1.0",
        )


def three_card_input(*, present_id: str = "major-01") -> TarotExperienceInput:
    return TarotExperienceInput(
        deck_id="dark_cosmic_archive",
        spread="three_card",
        cards=(
            TarotCardSelection(
                "major-02",
                "future",
                order=2,
                card_name="The High Priestess",
                meaning=("Quiet symbolic reflection.",),
            ),
            TarotCardSelection(
                "major-00",
                "past",
                order=0,
                card_name="The Fool",
                meaning=("An opening motif.",),
            ),
            TarotCardSelection(
                present_id,
                "present",
                order=1,
                card_name="The Magician",
                meaning=("Focused symbolic attention.",),
            ),
        ),
    )


def test_three_card_build_resolves_all_assets_in_past_present_future_order() -> None:
    resolver = RecordingResolver()
    result = TarotExperienceOrchestrator(resolver, DefaultAssetReferenceConsumer()).build(
        three_card_input()
    )

    assert result.spread == "three_card"
    assert [card.position.value for card in result.cards] == ["past", "present", "future"]
    assert resolver.calls == [
        ("dark_cosmic_archive", "major-00"),
        ("dark_cosmic_archive", "major-01"),
        ("dark_cosmic_archive", "major-02"),
    ]
    assert [resource.metadata["card_id"] for resource in result.display_resources] == [
        "major-00",
        "major-01",
        "major-02",
    ]
    assert [section.title for section in result.text_sections] == ["Past", "Present", "Future"]
    assert "The Fool" in result.text_sections[0].content
    assert "opening motif" in result.text_sections[0].content


def test_three_card_presentation_keeps_each_resource_adjacent_to_its_position_section() -> None:
    resolver = RecordingResolver()
    experience = TarotExperienceOrchestrator(
        resolver, DefaultAssetReferenceConsumer()
    ).build(three_card_input())

    presentation = ExperiencePresentationBuilder().build(experience, mode="full")
    message = PresentationResultMessageConverter().convert(presentation)

    assert [
        section.title for section in presentation.sections if isinstance(section, TextPresentation)
    ] == ["Title", "Past", "Present", "Future"]
    assert [
        section.resource.metadata["card_id"]
        for section in presentation.sections
        if isinstance(section, ImagePresentation)
    ] == ["major-00", "major-01", "major-02"]
    assert [section.title for section in message.sections] == ["Past", "Present", "Future"]
    assert [resource.metadata["card_id"] for resource in message.resources] == [
        "major-00",
        "major-01",
        "major-02",
    ]


def test_three_card_missing_asset_degrades_to_ordered_text_and_remaining_resources() -> None:
    resolver = RecordingResolver()
    result = TarotExperienceOrchestrator(resolver, DefaultAssetReferenceConsumer()).build(
        three_card_input(present_id="missing_card")
    )

    assert [resource.metadata["card_id"] for resource in result.display_resources] == [
        "major-00",
        "major-02",
    ]
    assert [section.title for section in result.text_sections] == ["Past", "Present", "Future"]
    assert "The Magician" in result.text_sections[1].content


def test_three_card_requires_all_positions_and_consecutive_orders() -> None:
    invalid_input = TarotExperienceInput(
        deck_id="dark_cosmic_archive",
        spread="three_card",
        cards=(
            TarotCardSelection("major-00", "past", order=0),
            TarotCardSelection("major-01", "present", order=2),
            TarotCardSelection("major-02", "future", order=3),
        ),
    )

    with pytest.raises(ExperienceInputError, match="consecutive order"):
        TarotExperienceOrchestrator(
            RecordingResolver(), DefaultAssetReferenceConsumer()
        ).build(invalid_input)
