"""Tests for v1/v2 Tool-result dispatch before platform-neutral Experience build."""

from __future__ import annotations

import json

import pytest
from starpath_plugin.core.resolver import AssetReference, AssetResolver
from starpath_plugin.experience.application import TarotExperienceApplication
from starpath_plugin.experience.asset_consumer import DefaultAssetReferenceConsumer
from starpath_plugin.experience.record_adapter import StarpathRecordExperienceAdapter
from starpath_plugin.experience.tarot import TarotExperienceOrchestrator
from starpath_plugin.experience.tool_contract_dispatcher import (
    STARPATH_TOOL_V1,
    StarpathToolContractDispatcher,
    StarpathToolContractDispatchError,
    V2TarotExperiencePayload,
)
from starpath_plugin.experience.tool_result_parser import StarpathToolResultParser
from starpath_plugin.models import StarpathRecord


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


def _base_payload() -> dict[str, object]:
    return {
        "record_id": "starpath-dispatch-test",
        "generated_at": "2026-08-22T00:00:00Z",
        "mode": "daily",
        "star": {
            "id": "sirius",
            "name": "Sirius",
            "zh_name": "天狼星",
            "type": "star",
            "astronomy": "A bright nearby stellar system.",
            "symbolism": "A cultural guiding symbol.",
        },
        "quote": {"id": "q1", "text": "Observe the sky.", "theme": "reflection"},
    }


def _v1_payload() -> dict[str, object]:
    payload = _base_payload()
    card = _card("major-00", "main", 0)
    card.pop("position")
    card.pop("order")
    payload["tarot"] = card
    payload["metadata"] = {"contract_version": STARPATH_TOOL_V1}
    return payload


def _v2_payload(*, spread: str = "three_card") -> dict[str, object]:
    payload = _base_payload()
    payload["tarot"] = {
        "spread": spread,
        "cards": [
            _card("major-00", "past", 0),
            _card("major-01", "present", 1),
            _card("major-02", "future", 2),
        ],
    }
    payload["metadata"] = {"contract_version": "starpath.tool.v2"}
    return payload


def _dispatcher() -> StarpathToolContractDispatcher:
    return StarpathToolContractDispatcher(StarpathToolResultParser())


class Resolver(AssetResolver):
    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        return AssetReference(
            deck_id=deck_id,
            card_id=card_id,
            asset_key=f"{deck_id}_{card_id}",
            path=f"major/{card_id}.png",
            format="png",
        )


def test_dispatcher_preserves_the_existing_v1_record_flow() -> None:
    parsed = _dispatcher().parse(json.dumps(_v1_payload()))

    assert isinstance(parsed, StarpathRecord)
    assert parsed.tarot.card.id == "major-00"
    assert parsed.tarot.orientation == "upright"


def test_dispatcher_maps_v2_single_card_to_existing_experience_input() -> None:
    payload = _v2_payload(spread="single")
    payload["tarot"]["cards"] = [_card("major-00", "main", 0)]

    parsed = _dispatcher().parse(json.dumps(payload))

    assert isinstance(parsed, V2TarotExperiencePayload)
    experience_input = parsed.to_experience_input("dark_cosmic_archive")
    assert experience_input.spread == "single"
    assert experience_input.cards[0].card_name == "Card major-00"
    assert experience_input.cards[0].meaning == ("symbolic meaning",)


def test_dispatcher_maps_v2_three_card_to_a_validated_ordered_spread() -> None:
    parsed = _dispatcher().parse(json.dumps(_v2_payload()))

    assert isinstance(parsed, V2TarotExperiencePayload)
    assert parsed.spread.spread_type.value == "three_card"
    assert [card.card_id for card in parsed.spread.cards] == [
        "major-00",
        "major-01",
        "major-02",
    ]
    assert [card.position.value for card in parsed.spread.cards] == [
        "past",
        "present",
        "future",
    ]


def test_v2_three_card_payload_flows_through_the_existing_experience_application() -> None:
    parsed = _dispatcher().parse(json.dumps(_v2_payload()))
    assert isinstance(parsed, V2TarotExperiencePayload)
    application = TarotExperienceApplication(
        StarpathRecordExperienceAdapter(),
        TarotExperienceOrchestrator(Resolver(), DefaultAssetReferenceConsumer()),
    )

    experience = application.build_input(parsed.to_experience_input("dark_cosmic_archive"))

    assert experience.spread == "three_card"
    assert [resource.metadata["card_id"] for resource in experience.display_resources] == [
        "major-00",
        "major-01",
        "major-02",
    ]
    assert [section.title for section in experience.text_sections] == [
        "Past",
        "Present",
        "Future",
        "Fortune sign",
    ]


@pytest.mark.parametrize(
    "payload",
    [
        _v2_payload(spread="unsupported_spread"),
        {**_v2_payload(), "tarot": {"spread": "three_card", "cards": []}},
    ],
)
def test_dispatcher_rejects_invalid_v2_spread_or_cards(payload: dict[str, object]) -> None:
    with pytest.raises(StarpathToolContractDispatchError):
        _dispatcher().parse(json.dumps(payload))
