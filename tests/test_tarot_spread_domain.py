"""Tests for expandable, platform-neutral Tarot spread domain models."""

from __future__ import annotations

import pytest
from starpath_plugin.experience.tarot import (
    CardPosition,
    ExperienceInputError,
    SpreadType,
    TarotCardSelection,
    TarotExperienceInput,
    TarotSpread,
)


def test_single_card_selection_remains_compatible_with_existing_string_inputs() -> None:
    selection = TarotCardSelection(card_id="major-00", position="main")
    experience_input = TarotExperienceInput(
        deck_id="dark_cosmic_archive",
        spread="single",
        cards=(selection,),
    )

    assert selection.position is CardPosition.MAIN
    assert selection.order == 0
    assert experience_input.spread == "single"
    assert experience_input.cards == (selection,)


def test_three_card_spread_models_past_present_future() -> None:
    spread = TarotSpread(
        spread_type=SpreadType.THREE_CARD,
        cards=(
            TarotCardSelection("major-00", CardPosition.PAST, order=0),
            TarotCardSelection("major-01", CardPosition.PRESENT, order=1),
            TarotCardSelection("major-02", CardPosition.FUTURE, order=2),
        ),
    )

    assert spread.spread_type is SpreadType.THREE_CARD
    assert [card.position for card in spread.cards] == [
        CardPosition.PAST,
        CardPosition.PRESENT,
        CardPosition.FUTURE,
    ]


def test_spread_sorts_card_selections_by_order_before_validating_shape() -> None:
    spread = TarotSpread(
        spread_type="three_card",
        cards=(
            TarotCardSelection("major-02", "future", order=2),
            TarotCardSelection("major-00", "past", order=0),
            TarotCardSelection("major-01", "present", order=1),
        ),
    )

    assert [card.card_id for card in spread.cards] == ["major-00", "major-01", "major-02"]


@pytest.mark.parametrize("position", ["unknown", "", None])
def test_unknown_or_empty_card_positions_are_rejected(position: object) -> None:
    with pytest.raises(ExperienceInputError):
        TarotCardSelection("major-00", position)  # type: ignore[arg-type]


def test_empty_cards_and_invalid_spread_shapes_are_rejected() -> None:
    with pytest.raises(ExperienceInputError):
        TarotSpread(SpreadType.SINGLE, ())
    with pytest.raises(ExperienceInputError):
        TarotSpread(
            SpreadType.THREE_CARD,
            (TarotCardSelection("major-00", CardPosition.MAIN),),
        )


def test_existing_input_retains_an_unknown_future_spread_for_later_orchestration_support() -> None:
    experience_input = TarotExperienceInput(
        deck_id="dark_cosmic_archive",
        spread="future_spread",
        cards=(TarotCardSelection("major-00", CardPosition.MAIN),),
    )

    assert experience_input.spread == "future_spread"
