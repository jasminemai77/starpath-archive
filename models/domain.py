"""Pure domain models for symbolic Starpath records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Star:
    """A real celestial object with a separate cultural interpretation."""

    id: str
    name: str
    zh_name: str
    type: str
    astronomy: str
    symbolism: str

    @property
    def chinese_name(self) -> str:
        """Compatibility alias retained for the Sprint 1 tool result."""
        return self.zh_name

    @property
    def category(self) -> str:
        """Compatibility alias retained for the Sprint 1 tool result."""
        return self.type


@dataclass(frozen=True)
class TarotCard:
    """A tarot card's traditional, non-predictive reference data."""

    id: str
    name: str
    zh_name: str
    number: int | str
    arcana: str
    suit: str | None
    keywords: tuple[str, ...]
    upright_meaning: tuple[str, ...]
    reversed_meaning: tuple[str, ...]
    symbolism: dict[str, str] = field(default_factory=dict)
    literary_material: tuple[str, ...] = ()
    image: str | None = None

    @property
    def chinese_name(self) -> str:
        """Compatibility alias retained for Sprint 1 consumers."""
        return self.zh_name


@dataclass(frozen=True)
class TarotDraw:
    """One card drawn in an orientation."""

    card: TarotCard
    orientation: str
    keywords: tuple[str, ...]
    meaning: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        card = asdict(self.card)
        card["keywords"] = list(self.card.keywords)
        card["upright_meaning"] = list(self.card.upright_meaning)
        card["reversed_meaning"] = list(self.card.reversed_meaning)
        card["literary_material"] = list(self.card.literary_material)
        card["chinese_name"] = self.card.chinese_name
        return {
            **card,
            "orientation": self.orientation,
            "draw_keywords": list(self.keywords),
            "meaning": list(self.meaning),
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
        star = asdict(self.star)
        star["chinese_name"] = self.star.chinese_name
        star["category"] = self.star.category
        return {
            "record_id": self.record_id,
            "star": star,
            "tarot": self.tarot.as_dict(),
            "quote": asdict(self.quote),
        }
