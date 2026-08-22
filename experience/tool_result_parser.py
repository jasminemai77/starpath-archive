"""Extract and parse the stable ``starpath.tool.v1`` result without delivery work."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from ..models import Quote, Star, StarpathRecord, TarotCard, TarotDraw


class InvalidStarpathToolResultError(ValueError):
    """Raised when required ``starpath.tool.v1`` data is absent or malformed."""


class MissingTarotCardError(InvalidStarpathToolResultError):
    """Raised when the result cannot identify its selected Tarot card."""


class ToolResultExtractionError(InvalidStarpathToolResultError):
    """Raised when an AstrBot ``CallToolResult`` has no usable text content."""


class ToolResultExtractor:
    """Extract JSON text from AstrBot's MCP ``CallToolResult`` shape only.

    The extractor deliberately knows no Starpath field names.  It accepts the
    structural ``content: [TextContent(...)]`` contract supplied by AstrBot and
    passes the untouched text to the platform-neutral parser.
    """

    def extract(self, result: object) -> str:
        if result is None:
            raise ToolResultExtractionError("Tool result is missing")
        content = getattr(result, "content", None)
        if not isinstance(content, Sequence) or isinstance(content, (str, bytes)):
            raise ToolResultExtractionError("Tool result has invalid content")
        if not content:
            raise ToolResultExtractionError("Tool result has no content")

        first = content[0]
        if getattr(first, "type", None) != "text":
            raise ToolResultExtractionError("Tool result has no text content")
        text = getattr(first, "text", None)
        if not isinstance(text, str) or not text.strip():
            raise ToolResultExtractionError("Tool result has no text content")
        return text


class StarpathToolResultParser:
    """Rebuild a complete domain record from a raw ``starpath.tool.v1`` JSON string."""

    def parse(self, raw: str) -> StarpathRecord:
        if not isinstance(raw, str):
            raise InvalidStarpathToolResultError("Expected JSON text")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise InvalidStarpathToolResultError("Invalid JSON") from error
        if not isinstance(value, dict):
            raise InvalidStarpathToolResultError("Expected JSON object")
        record_id = self._required_string(value, "record_id", "result")
        star = self._star(self._required_mapping(value, "star", "result"))
        tarot = self._tarot(self._required_mapping(value, "tarot", "result"))
        quote = self._quote(self._required_mapping(value, "quote", "result"))
        return StarpathRecord(record_id, star, tarot, quote)

    @classmethod
    def _star(cls, value: Mapping[str, Any]) -> Star:
        return Star(
            id=cls._required_string(value, "id", "star"),
            name=cls._required_string(value, "name", "star"),
            zh_name=cls._required_alias(value, "zh_name", "chinese_name", "star"),
            type=cls._required_alias(value, "type", "category", "star"),
            astronomy=cls._required_string(value, "astronomy", "star"),
            symbolism=cls._required_string(value, "symbolism", "star"),
        )

    @classmethod
    def _tarot(cls, value: Mapping[str, Any]) -> TarotDraw:
        card_id = value.get("id")
        if not isinstance(card_id, str) or not card_id.strip():
            raise MissingTarotCardError("Tarot result requires a non-empty 'id'")

        number = value.get("number")
        if not isinstance(number, (int, str)) or isinstance(number, bool):
            raise InvalidStarpathToolResultError("Tarot requires 'number'")
        suit = value.get("suit")
        if suit is not None and not isinstance(suit, str):
            raise InvalidStarpathToolResultError("Tarot 'suit' must be a string or null")

        symbolism = value.get("symbolism", {})
        if not isinstance(symbolism, Mapping) or not all(
            isinstance(key, str) and isinstance(item, str)
            for key, item in symbolism.items()
        ):
            raise InvalidStarpathToolResultError("Tarot 'symbolism' must be a string map")

        card = TarotCard(
            id=card_id,
            name=cls._required_string(value, "name", "tarot"),
            zh_name=cls._required_alias(value, "zh_name", "chinese_name", "tarot"),
            number=number,
            arcana=cls._required_string(value, "arcana", "tarot"),
            suit=suit,
            keywords=cls._required_strings(value, "keywords", "tarot"),
            upright_meaning=cls._required_strings(value, "upright_meaning", "tarot"),
            reversed_meaning=cls._required_strings(value, "reversed_meaning", "tarot"),
            symbolism=dict(symbolism),
            literary_material=cls._optional_strings(value, "literary_material", "tarot"),
            image=cls._optional_string(value, "image", "tarot"),
        )
        return TarotDraw(
            card=card,
            orientation=cls._required_string(value, "orientation", "tarot"),
            keywords=cls._required_strings(value, "draw_keywords", "tarot"),
            meaning=cls._required_strings(value, "meaning", "tarot"),
        )

    @classmethod
    def _quote(cls, value: Mapping[str, Any]) -> Quote:
        return Quote(
            id=cls._required_string(value, "id", "quote"),
            text=cls._required_string(value, "text", "quote"),
            theme=cls._required_string(value, "theme", "quote"),
        )

    @staticmethod
    def _required_mapping(
        value: Mapping[str, Any], field: str, location: str
    ) -> Mapping[str, Any]:
        item = value.get(field)
        if not isinstance(item, Mapping):
            raise InvalidStarpathToolResultError(f"{location} requires object '{field}'")
        return item

    @staticmethod
    def _required_string(value: Mapping[str, Any], field: str, location: str) -> str:
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            raise InvalidStarpathToolResultError(f"{location} requires non-empty '{field}'")
        return item

    @classmethod
    def _required_alias(
        cls, value: Mapping[str, Any], primary: str, alias: str, location: str
    ) -> str:
        item = value.get(primary, value.get(alias))
        if not isinstance(item, str) or not item.strip():
            raise InvalidStarpathToolResultError(
                f"{location} requires non-empty '{primary}'"
            )
        return item

    @staticmethod
    def _required_strings(
        value: Mapping[str, Any], field: str, location: str
    ) -> tuple[str, ...]:
        item = value.get(field)
        if not isinstance(item, list) or not all(
            isinstance(entry, str) and entry.strip() for entry in item
        ):
            raise InvalidStarpathToolResultError(f"{location} requires string list '{field}'")
        return tuple(item)

    @classmethod
    def _optional_strings(
        cls, value: Mapping[str, Any], field: str, location: str
    ) -> tuple[str, ...]:
        if field not in value:
            return ()
        return cls._required_strings(value, field, location)

    @staticmethod
    def _optional_string(
        value: Mapping[str, Any], field: str, location: str
    ) -> str | None:
        if field not in value or value[field] is None:
            return None
        return StarpathToolResultParser._required_string(value, field, location)
