"""Tests for the unregistered, injectable ``starpath.tool.v2`` producer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from starpath_plugin.contracts.starpath_tool_v2 import (
    FUTURE_STARPATH_TOOL_V2,
    FutureStarpathToolV2Parser,
)
from starpath_plugin.core.tool_v2_producer import (
    StarpathToolV2Producer,
    V2ToolProducerError,
)
from starpath_plugin.models import Quote, Star, TarotCard, TarotDraw


class FixedDrawProvider:
    def __init__(self, draws: list[TarotDraw]) -> None:
        self._draws = iter(draws)
        self.calls = 0

    def draw(self) -> TarotDraw:
        self.calls += 1
        return next(self._draws)


def _draw(card_id: str, orientation: str = "upright") -> TarotDraw:
    card = TarotCard(
        id=card_id,
        name=f"Card {card_id}",
        zh_name="示例牌",
        number=0,
        arcana="major",
        suit=None,
        keywords=("symbol",),
        upright_meaning=("upright meaning",),
        reversed_meaning=("reversed meaning",),
        symbolism={"motif": "archive"},
    )
    meaning = card.upright_meaning if orientation == "upright" else card.reversed_meaning
    return TarotDraw(card, orientation, card.keywords, meaning)


def _star() -> Star:
    return Star(
        id="sirius",
        name="Sirius",
        zh_name="天狼星",
        type="star",
        astronomy="A bright nearby stellar system.",
        symbolism="A cultural symbol of guidance.",
    )


def _quote() -> Quote:
    return Quote("q1", "Observe the sky.", "reflection")


def _producer(draws: list[TarotDraw]) -> tuple[StarpathToolV2Producer, FixedDrawProvider]:
    provider = FixedDrawProvider(draws)
    producer = StarpathToolV2Producer(
        provider,
        now=lambda: datetime(2026, 8, 22, 9, 30, tzinfo=timezone.utc),
        record_id_factory=lambda: "starpath-v2-test",
    )
    return producer, provider


def test_producer_builds_a_schema_valid_v2_single_result() -> None:
    producer, provider = _producer([_draw("major-00")])

    payload = producer.build(star=_star(), quote=_quote(), spread="single")

    assert payload["record_id"] == "starpath-v2-test"
    assert payload["generated_at"] == "2026-08-22T09:30:00Z"
    assert payload["metadata"]["contract_version"] == FUTURE_STARPATH_TOOL_V2
    assert payload["tarot"]["spread"] == "single"
    assert payload["tarot"]["cards"][0]["position"] == "main"
    assert payload["tarot"]["cards"][0]["order"] == 0
    assert provider.calls == 1
    assert FutureStarpathToolV2Parser().parse(payload).tarot.spread == "single"


def test_producer_builds_a_schema_valid_v2_three_card_result() -> None:
    producer, provider = _producer(
        [_draw("major-00"), _draw("major-01", "reversed"), _draw("major-02")]
    )

    payload = producer.build(star=_star(), quote=_quote(), spread="three_card")

    cards = payload["tarot"]["cards"]
    assert [(card["position"], card["order"]) for card in cards] == [
        ("past", 0),
        ("present", 1),
        ("future", 2),
    ]
    assert [card["id"] for card in cards] == ["major-00", "major-01", "major-02"]
    assert cards[1]["orientation"] == "reversed"
    assert provider.calls == 3
    assert FutureStarpathToolV2Parser().parse(payload).tarot.cards[2].position == "future"


@pytest.mark.parametrize("spread", ["", "three", "celtic_cross"])
def test_producer_rejects_unsupported_spreads_before_drawing(spread: str) -> None:
    producer, provider = _producer([_draw("major-00")])

    with pytest.raises(V2ToolProducerError, match="spread"):
        producer.build(star=_star(), quote=_quote(), spread=spread)

    assert provider.calls == 0


def test_producer_requires_draw_provider_to_return_complete_draws() -> None:
    class InvalidDrawProvider:
        def draw(self) -> object:
            return object()

    producer = StarpathToolV2Producer(InvalidDrawProvider())  # type: ignore[arg-type]

    with pytest.raises(V2ToolProducerError, match="TarotDraw"):
        producer.build(star=_star(), quote=_quote(), spread="single")
