"""Validation models for the future ``starpath.tool.v2`` contract.

This module is intentionally isolated from the current Native Tool, runtime,
and experience pipeline.  It validates producer and consumer payloads behind
an explicit contract version without activating a new Native Tool.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

FUTURE_STARPATH_TOOL_V2 = "starpath.tool.v2"
_SUPPORTED_POSITIONS = frozenset({"main", "past", "present", "future"})


class FutureStarpathToolContractError(ValueError):
    """Raised when a proposed v2 payload is incomplete or structurally invalid."""


@dataclass(frozen=True)
class FutureStar:
    """The unchanged factual/symbolic celestial object carried by v2."""

    id: str
    name: str
    zh_name: str
    type: str
    astronomy: str
    symbolism: str


@dataclass(frozen=True)
class FutureQuote:
    """The unchanged cultural quote object carried by v2."""

    id: str
    text: str
    theme: str


@dataclass(frozen=True)
class FutureTarotCard:
    """One complete drawn card plus its ordered spread position."""

    id: str
    name: str
    zh_name: str
    number: int | str
    arcana: str
    suit: str | None
    keywords: tuple[str, ...]
    upright_meaning: tuple[str, ...]
    reversed_meaning: tuple[str, ...]
    symbolism: Mapping[str, str]
    literary_material: tuple[str, ...]
    image: str | None
    orientation: str
    draw_keywords: tuple[str, ...]
    meaning: tuple[str, ...]
    position: str
    order: int


@dataclass(frozen=True)
class FutureTarotSpread:
    """The v2 Tarot envelope, replacing v1's single flattened draw."""

    spread: str
    cards: tuple[FutureTarotCard, ...]


@dataclass(frozen=True)
class FutureStarpathToolResult:
    """A fully validated representation of the proposed v2 JSON result."""

    record_id: str
    generated_at: str
    mode: str
    star: FutureStar
    tarot: FutureTarotSpread
    quote: FutureQuote
    metadata: Mapping[str, object]


class FutureStarpathToolV2Parser:
    """Parse v2 schema payloads without activating a new Native Tool.

    Unknown fields are deliberately accepted so additive future fields do not
    invalidate a compatible client.  Required fields and the v2 card-position
    vocabulary remain strict.
    """

    def parse(self, raw: str | Mapping[str, object]) -> FutureStarpathToolResult:
        value = self._decode(raw)
        metadata = self._required_mapping(value, "metadata", "result")
        if metadata.get("contract_version") != FUTURE_STARPATH_TOOL_V2:
            raise FutureStarpathToolContractError(
                f"result requires contract_version '{FUTURE_STARPATH_TOOL_V2}'"
            )

        return FutureStarpathToolResult(
            record_id=self._required_string(value, "record_id", "result"),
            generated_at=self._required_string(value, "generated_at", "result"),
            mode=self._required_string(value, "mode", "result"),
            star=self._star(self._required_mapping(value, "star", "result")),
            tarot=self._tarot(self._required_mapping(value, "tarot", "result")),
            quote=self._quote(self._required_mapping(value, "quote", "result")),
            metadata=dict(metadata),
        )

    @classmethod
    def _decode(cls, raw: str | Mapping[str, object]) -> Mapping[str, object]:
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError as error:
                raise FutureStarpathToolContractError("Invalid JSON") from error
        if not isinstance(raw, Mapping):
            raise FutureStarpathToolContractError("Expected JSON object")
        return raw

    @classmethod
    def _star(cls, value: Mapping[str, object]) -> FutureStar:
        return FutureStar(
            id=cls._required_string(value, "id", "star"),
            name=cls._required_string(value, "name", "star"),
            zh_name=cls._required_string(value, "zh_name", "star"),
            type=cls._required_string(value, "type", "star"),
            astronomy=cls._required_string(value, "astronomy", "star"),
            symbolism=cls._required_string(value, "symbolism", "star"),
        )

    @classmethod
    def _tarot(cls, value: Mapping[str, object]) -> FutureTarotSpread:
        spread = cls._required_string(value, "spread", "tarot")
        raw_cards = value.get("cards")
        if not isinstance(raw_cards, list) or not raw_cards:
            raise FutureStarpathToolContractError("tarot requires non-empty list 'cards'")
        if not all(isinstance(card, Mapping) for card in raw_cards):
            raise FutureStarpathToolContractError("tarot cards must be objects")

        cards = tuple(cls._card(card) for card in raw_cards)
        if len({card.order for card in cards}) != len(cards):
            raise FutureStarpathToolContractError("tarot card orders must be unique")
        ordered_cards = tuple(sorted(cards, key=lambda card: card.order))
        cls._validate_known_spread_shape(spread, ordered_cards)
        return FutureTarotSpread(spread=spread, cards=ordered_cards)

    @staticmethod
    def _validate_known_spread_shape(
        spread: str, cards: tuple[FutureTarotCard, ...]
    ) -> None:
        expected_positions = {
            "single": ("main",),
            "three_card": ("past", "present", "future"),
        }.get(spread)
        if expected_positions is None:
            return
        if tuple(card.position for card in cards) != expected_positions:
            raise FutureStarpathToolContractError(
                f"{spread} tarot spread requires positions {list(expected_positions)} in order"
            )

    @classmethod
    def _card(cls, value: Mapping[str, object]) -> FutureTarotCard:
        position = cls._required_string(value, "position", "tarot card")
        if position not in _SUPPORTED_POSITIONS:
            raise FutureStarpathToolContractError("tarot card requires a known position")

        number = value.get("number")
        if not isinstance(number, (int, str)) or isinstance(number, bool):
            raise FutureStarpathToolContractError("tarot card requires 'number'")
        suit = value.get("suit")
        if suit is not None and not isinstance(suit, str):
            raise FutureStarpathToolContractError("tarot card 'suit' must be string or null")
        order = value.get("order")
        if not isinstance(order, int) or isinstance(order, bool) or order < 0:
            raise FutureStarpathToolContractError("tarot card requires non-negative 'order'")

        symbolism = cls._required_mapping(value, "symbolism", "tarot card")
        if not all(
            isinstance(key, str) and isinstance(item, str)
            for key, item in symbolism.items()
        ):
            raise FutureStarpathToolContractError("tarot card 'symbolism' must be a string map")

        return FutureTarotCard(
            id=cls._required_string(value, "id", "tarot card"),
            name=cls._required_string(value, "name", "tarot card"),
            zh_name=cls._required_string(value, "zh_name", "tarot card"),
            number=number,
            arcana=cls._required_string(value, "arcana", "tarot card"),
            suit=suit,
            keywords=cls._required_strings(value, "keywords", "tarot card"),
            upright_meaning=cls._required_strings(value, "upright_meaning", "tarot card"),
            reversed_meaning=cls._required_strings(value, "reversed_meaning", "tarot card"),
            symbolism=dict(symbolism),
            literary_material=cls._optional_strings(value, "literary_material", "tarot card"),
            image=cls._optional_string(value, "image", "tarot card"),
            orientation=cls._required_string(value, "orientation", "tarot card"),
            draw_keywords=cls._required_strings(value, "draw_keywords", "tarot card"),
            meaning=cls._required_strings(value, "meaning", "tarot card"),
            position=position,
            order=order,
        )

    @classmethod
    def _quote(cls, value: Mapping[str, object]) -> FutureQuote:
        return FutureQuote(
            id=cls._required_string(value, "id", "quote"),
            text=cls._required_string(value, "text", "quote"),
            theme=cls._required_string(value, "theme", "quote"),
        )

    @staticmethod
    def _required_mapping(
        value: Mapping[str, object], field: str, location: str
    ) -> Mapping[str, Any]:
        item = value.get(field)
        if not isinstance(item, Mapping):
            raise FutureStarpathToolContractError(f"{location} requires object '{field}'")
        return item

    @staticmethod
    def _required_string(value: Mapping[str, object], field: str, location: str) -> str:
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            raise FutureStarpathToolContractError(f"{location} requires non-empty '{field}'")
        return item

    @staticmethod
    def _required_strings(
        value: Mapping[str, object], field: str, location: str
    ) -> tuple[str, ...]:
        item = value.get(field)
        if not isinstance(item, list) or not all(
            isinstance(entry, str) and entry.strip() for entry in item
        ):
            raise FutureStarpathToolContractError(
                f"{location} requires string list '{field}'"
            )
        return tuple(item)

    @classmethod
    def _optional_strings(
        cls, value: Mapping[str, object], field: str, location: str
    ) -> tuple[str, ...]:
        if field not in value:
            return ()
        return cls._required_strings(value, field, location)

    @staticmethod
    def _optional_string(
        value: Mapping[str, object], field: str, location: str
    ) -> str | None:
        if field not in value or value[field] is None:
            return None
        return FutureStarpathToolV2Parser._required_string(value, field, location)
