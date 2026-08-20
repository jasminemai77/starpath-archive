from __future__ import annotations

from datetime import date

import pytest
from starpath_plugin.core import (
    QuoteEngine,
    StarEngine,
    StarpathService,
    TarotEngine,
    ValidationError,
)
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards


def build_service() -> StarpathService:
    return StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )


def test_static_data_is_complete_for_sprint_one() -> None:
    stars = load_stars()
    cards = load_tarot_cards()
    quotes = load_quotes()

    assert 10 <= len(stars) <= 20
    assert len(cards) >= 22
    assert {card.arcana for card in cards} == {"major"}
    assert len(quotes) >= 30
    assert all(star.astronomy and star.symbolism for star in stars)


def test_same_user_and_day_always_selects_the_same_star() -> None:
    engine = StarEngine(load_stars())
    selected = [
        engine.select_daily_star("hash-for-user-a", date(2026, 8, 20)).id for _ in range(10)
    ]

    assert len(set(selected)) == 1


def test_different_users_can_receive_different_daily_stars() -> None:
    engine = StarEngine(load_stars())
    ids = {engine.select_daily_star(f"user-{index}", date(2026, 8, 20)).id for index in range(50)}

    assert len(ids) > 1


def test_service_generates_a_complete_symbolic_record() -> None:
    record = build_service().generate(
        user_hash="hash-for-user-a", on_date=date(2026, 8, 20), mode="daily", spread="single"
    )

    payload = record.as_dict()
    assert payload["record_id"].startswith("starpath-")
    assert payload["star"]["id"]
    assert payload["tarot"]["orientation"] in {"upright", "reversed"}
    assert payload["quote"]["text"]


@pytest.mark.parametrize(("mode", "spread"), [("weekly", "single"), ("daily", "three")])
def test_service_rejects_unsupported_parameters(mode: str, spread: str) -> None:
    with pytest.raises(ValidationError):
        build_service().generate(
            user_hash="hash-for-user-a", on_date=date(2026, 8, 20), mode=mode, spread=spread
        )
