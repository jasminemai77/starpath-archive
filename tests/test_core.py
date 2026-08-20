from __future__ import annotations

from collections import Counter
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


def test_static_data_is_complete_for_sprint_two() -> None:
    stars = load_stars()
    cards = load_tarot_cards()
    quotes = load_quotes()

    assert len(stars) >= 50
    assert len(cards) == 78
    assert Counter(card.arcana for card in cards) == {"major": 22, "minor": 56}
    assert len(quotes) >= 30
    assert all(star.astronomy and star.symbolism for star in stars)


def test_astral_dataset_has_supported_types_required_fields_and_unique_ids() -> None:
    stars = load_stars()
    type_counts = Counter(star.type for star in stars)

    assert type_counts == {"star": 27, "cluster": 7, "nebula": 8, "galaxy": 8}
    assert len({star.id for star in stars}) == len(stars)
    for star in stars:
        assert star.id and star.name and star.zh_name
        assert star.astronomy and star.symbolism


def test_star_record_keeps_sprint_one_aliases_while_exposing_new_fields() -> None:
    record = build_service().generate(
        user_hash="hash-for-user-a", on_date=date(2026, 8, 20), mode="daily", spread="single"
    )
    star = record.as_dict()["star"]

    assert star["zh_name"] == star["chinese_name"]
    assert star["type"] == star["category"]


def test_complete_tarot_dataset_has_each_minor_suit_and_required_fields() -> None:
    cards = load_tarot_cards()
    suit_counts = Counter(card.suit for card in cards if card.arcana == "minor")

    assert suit_counts == {"wands": 14, "cups": 14, "swords": 14, "pentacles": 14}
    assert len({card.id for card in cards}) == 78
    for card in cards:
        assert card.id and card.name and card.zh_name
        assert card.keywords and card.upright_meaning and card.reversed_meaning
    assert all(
        card.symbolism and card.literary_material for card in cards if card.arcana == "minor"
    )


def test_tarot_draw_keeps_the_sprint_one_chinese_name_alias() -> None:
    draw = TarotEngine(load_tarot_cards()).draw().as_dict()

    assert draw["zh_name"] == draw["chinese_name"]
    assert isinstance(draw["meaning"], list)


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
