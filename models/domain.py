"""Pure domain models for symbolic Starpath records."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Star:
    """A real celestial object with a separate cultural interpretation."""

    id: str
    name: str
    chinese_name: str
    category: str
    astronomy: str
    symbolism: str


@dataclass(frozen=True)
class TarotCard:
    """A tarot card's traditional, non-predictive reference data."""

    id: str
    name: str
    chinese_name: str
    number: int | str
    arcana: str
    keywords: tuple[str, ...]
    upright_meaning: str
    reversed_meaning: str
    image: str | None = None


@dataclass(frozen=True)
class TarotDraw:
    """One card drawn in an orientation."""

    card: TarotCard
    orientation: str
    keywords: tuple[str, ...]
    meaning: str

    def as_dict(self) -> dict[str, object]:
        card = asdict(self.card)
        card["keywords"] = list(self.card.keywords)
        return {
            **card,
            "orientation": self.orientation,
            "draw_keywords": list(self.keywords),
            "meaning": self.meaning,
        }


@dataclass(frozen=True)
class Quote:
    id: str
    text: str
    theme: str


@dataclass(frozen=True)
class StarpathRecord:
    """A complete symbolic record, intended for Native Agent synthesis."""

    record_id: str
    star: Star
    tarot: TarotDraw
    quote: Quote

    def as_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "star": asdict(self.star),
            "tarot": self.tarot.as_dict(),
            "quote": asdict(self.quote),
        }
