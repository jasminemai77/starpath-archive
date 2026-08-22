"""Design-time checks for the future, multi-card ``starpath.tool.v2`` schema."""

from __future__ import annotations

import copy

import pytest
from starpath_plugin.contracts.starpath_tool_v2 import (
    FUTURE_STARPATH_TOOL_V2,
    FutureStarpathToolContractError,
    FutureStarpathToolV2Parser,
)


def _card(card_id: str, position: str, order: int) -> dict[str, object]:
    return {
        "id": card_id,
        "name": f"Card {card_id}",
        "zh_name": "示例牌",
        "number": 0,
        "arcana": "major",
        "suit": None,
        "keywords": ["symbol"],
        "upright_meaning": ["upright"],
        "reversed_meaning": ["reversed"],
        "symbolism": {"motif": "archive"},
        "literary_material": [],
        "image": None,
        "orientation": "upright",
        "draw_keywords": ["selected"],
        "meaning": ["symbolic meaning"],
        "position": position,
        "order": order,
    }


def _payload(cards: list[dict[str, object]], spread: str = "single") -> dict[str, object]:
    return {
        "record_id": "starpath-example",
        "generated_at": "2026-08-22T00:00:00Z",
        "mode": "daily",
        "star": {
            "id": "sirius",
            "name": "Sirius",
            "zh_name": "天狼星",
            "type": "star",
            "astronomy": "A bright nearby stellar system.",
            "symbolism": "A cultural symbol of guidance.",
        },
        "tarot": {"spread": spread, "cards": cards},
        "quote": {"id": "q1", "text": "Observe the sky.", "theme": "reflection"},
        "metadata": {
            "contract_version": FUTURE_STARPATH_TOOL_V2,
            "content_scope": "symbolic_entertainment",
        },
    }


def test_v2_single_card_retains_the_full_v1_draw_semantics() -> None:
    result = FutureStarpathToolV2Parser().parse(_payload([_card("major-00", "main", 0)]))

    assert result.tarot.spread == "single"
    assert result.tarot.cards[0].id == "major-00"
    assert result.tarot.cards[0].orientation == "upright"
    assert result.tarot.cards[0].draw_keywords == ("selected",)
    assert result.tarot.cards[0].meaning == ("symbolic meaning",)
    assert result.tarot.cards[0].position == "main"


def test_v2_three_card_spread_sorts_and_preserves_semantic_positions() -> None:
    payload = _payload(
        [
            _card("major-02", "future", 2),
            _card("major-00", "past", 0),
            _card("major-01", "present", 1),
        ],
        spread="three_card",
    )

    result = FutureStarpathToolV2Parser().parse(payload)

    assert [card.id for card in result.tarot.cards] == ["major-00", "major-01", "major-02"]
    assert [card.position for card in result.tarot.cards] == ["past", "present", "future"]


def test_v2_rejects_a_known_spread_with_the_wrong_card_shape() -> None:
    with pytest.raises(FutureStarpathToolContractError, match="three_card"):
        FutureStarpathToolV2Parser().parse(_payload([_card("major-00", "main", 0)], "three_card"))


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (lambda payload: payload["tarot"].pop("cards"), "cards"),
        (lambda payload: payload["tarot"]["cards"][0].pop("id"), "id"),
        (lambda payload: payload.pop("quote"), "quote"),
    ],
)
def test_v2_rejects_missing_required_fields(mutator, expected: str) -> None:
    payload = _payload([_card("major-00", "main", 0)])
    mutator(payload)

    with pytest.raises(FutureStarpathToolContractError, match=expected):
        FutureStarpathToolV2Parser().parse(payload)


@pytest.mark.parametrize("position", ["unknown", "", "past-tense"])
def test_v2_rejects_invalid_positions(position: str) -> None:
    with pytest.raises(FutureStarpathToolContractError, match="position"):
        FutureStarpathToolV2Parser().parse(_payload([_card("major-00", position, 0)]))


def test_v2_accepts_additive_future_fields_without_changing_required_semantics() -> None:
    payload = copy.deepcopy(_payload([_card("major-00", "main", 0)]))
    payload["future_root_field"] = {"revision": 2}
    payload["tarot"]["future_tarot_field"] = True
    payload["tarot"]["cards"][0]["future_card_field"] = "accepted"

    result = FutureStarpathToolV2Parser().parse(payload)

    assert result.record_id == "starpath-example"
    assert result.tarot.cards[0].id == "major-00"
