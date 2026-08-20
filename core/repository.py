"""Read-only repositories backed by package-local JSON data."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import Quote, Star, TarotCard

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _read_data(filename: str) -> list[dict[str, object]]:
    with (DATA_DIR / filename).open(encoding="utf-8") as source:
        value = json.load(source)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{filename} must contain a non-empty JSON array")
    return value


def load_stars() -> tuple[Star, ...]:
    return tuple(Star(**item) for item in _read_data("stars.json"))


def load_tarot_cards() -> tuple[TarotCard, ...]:
    return tuple(
        TarotCard(**{**item, "keywords": tuple(item["keywords"])})
        for item in _read_data("tarot.json")
    )


def load_quotes() -> tuple[Quote, ...]:
    return tuple(Quote(**item) for item in _read_data("quotes.json"))
