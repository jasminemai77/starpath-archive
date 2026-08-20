"""Deterministic daily-star and random symbolic-draw application services."""

from __future__ import annotations

from datetime import date
from hashlib import sha256
from secrets import choice, randbelow
from uuid import uuid4

from ..models import Quote, Star, StarpathRecord, TarotCard, TarotDraw


class ValidationError(ValueError):
    """Raised when a requested Starpath format is unsupported."""


class StarEngine:
    """Choose a stable daily star using only a caller hash and calendar date."""

    def __init__(self, stars: tuple[Star, ...]) -> None:
        if not stars:
            raise ValueError("StarEngine requires at least one star")
        self._stars = stars

    def select_daily_star(self, user_hash: str, on_date: date) -> Star:
        if not isinstance(user_hash, str) or not user_hash.strip():
            raise ValidationError("user_hash must be a non-empty string")
        seed = f"{user_hash.strip()}:{on_date.isoformat()}".encode("utf-8")
        index = int.from_bytes(sha256(seed).digest(), "big") % len(self._stars)
        return self._stars[index]


class TarotEngine:
    """Draw a traditional card and orientation without making a prediction."""

    def __init__(self, cards: tuple[TarotCard, ...]) -> None:
        if not cards:
            raise ValueError("TarotEngine requires at least one tarot card")
        self._cards = cards

    def draw(self) -> TarotDraw:
        card = self._cards[randbelow(len(self._cards))]
        orientation = choice(("upright", "reversed"))
        meaning = card.upright_meaning if orientation == "upright" else card.reversed_meaning
        return TarotDraw(
            card=card, orientation=orientation, keywords=card.keywords, meaning=meaning
        )


class QuoteEngine:
    def __init__(self, quotes: tuple[Quote, ...]) -> None:
        if not quotes:
            raise ValueError("QuoteEngine requires at least one quote")
        self._quotes = quotes

    def draw(self) -> Quote:
        return self._quotes[randbelow(len(self._quotes))]


class StarpathService:
    """Combine independently selected symbols into one record."""

    def __init__(
        self, star_engine: StarEngine, tarot_engine: TarotEngine, quote_engine: QuoteEngine
    ) -> None:
        self._star_engine = star_engine
        self._tarot_engine = tarot_engine
        self._quote_engine = quote_engine

    def generate(self, *, user_hash: str, on_date: date, mode: str, spread: str) -> StarpathRecord:
        if mode != "daily":
            raise ValidationError("mode must be 'daily'")
        if spread != "single":
            raise ValidationError("spread must be 'single'")
        return StarpathRecord(
            record_id=f"starpath-{uuid4().hex}",
            star=self._star_engine.select_daily_star(user_hash, on_date),
            tarot=self._tarot_engine.draw(),
            quote=self._quote_engine.draw(),
        )
