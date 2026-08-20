"""Read-only repositories backed by package-local JSON data."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import Quote, Star, TarotCard

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _read_data(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as source:
        value = json.load(source)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{path.name} must contain a non-empty JSON array")
    return value


def load_stars() -> tuple[Star, ...]:
    paths = (DATA_DIR / "stars.json", *sorted((DATA_DIR / "stars").glob("*.json")))
    stars: list[Star] = []
    legacy_type_map = {"open_cluster": "cluster", "star_pair": "star"}
    for path in paths:
        for item in _read_data(path):
            raw = dict(item)
            raw["zh_name"] = raw.pop("zh_name", None) or raw.pop("chinese_name", None)
            raw["type"] = raw.pop("type", None) or raw.pop("category", None)
            raw["type"] = legacy_type_map.get(raw["type"], raw["type"])
            stars.append(Star(**raw))
    return tuple(stars)


def load_tarot_cards() -> tuple[TarotCard, ...]:
    paths = (DATA_DIR / "tarot.json", *sorted((DATA_DIR / "tarot").glob("*.json")))
    cards: list[TarotCard] = []
    for path in paths:
        for item in _read_data(path):
            raw = dict(item)
            raw["zh_name"] = raw.pop("zh_name", raw.pop("chinese_name", None))
            raw.setdefault("suit", None)
            raw.setdefault("symbolism", {})
            raw.setdefault("literary_material", ())
            raw["keywords"] = tuple(raw["keywords"])
            raw["upright_meaning"] = _meaning_tuple(raw["upright_meaning"])
            raw["reversed_meaning"] = _meaning_tuple(raw["reversed_meaning"])
            raw["literary_material"] = tuple(raw["literary_material"])
            cards.append(TarotCard(**raw))
    return tuple(cards)


def _meaning_tuple(value: object) -> tuple[str, ...]:
    """Accept Sprint 1 strings while normalizing Sprint 2 meaning lists."""
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ValueError("tarot meanings must be a string or a list of strings")


def load_quotes() -> tuple[Quote, ...]:
    return tuple(Quote(**item) for item in _read_data(DATA_DIR / "quotes.json"))
