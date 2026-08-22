"""Version-aware, platform-neutral dispatch for captured Starpath Tool JSON."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

from ..contracts.starpath_tool_v2 import (
    FUTURE_STARPATH_TOOL_V2,
    FutureStarpathToolContractError,
    FutureStarpathToolResult,
    FutureStarpathToolV2Parser,
)
from ..models import StarpathRecord
from .tarot import (
    FortuneContext,
    TarotCardSelection,
    TarotExperienceInput,
    TarotSpread,
)
from .tool_result_parser import StarpathToolResultParser

STARPATH_TOOL_V1 = "starpath.tool.v1"


class StarpathToolContractDispatchError(ValueError):
    """Raised when captured Tool JSON has no supported contract version."""


@dataclass(frozen=True)
class V2TarotExperiencePayload:
    """V2's platform-neutral Experience data before a deck is injected."""

    spread: TarotSpread
    fortune_context: FortuneContext

    @classmethod
    def from_contract(cls, result: FutureStarpathToolResult) -> "V2TarotExperiencePayload":
        """Map complete v2 card draws into the existing logical spread domain."""
        selections = tuple(
            TarotCardSelection(
                card_id=card.id,
                position=card.position,
                order=card.order,
                card_name=card.name,
                meaning=card.meaning,
            )
            for card in result.tarot.cards
        )
        return cls(
            spread=TarotSpread(result.tarot.spread, selections),
            fortune_context=FortuneContext(
                quote_id=result.quote.id,
                text=result.quote.text,
                theme=result.quote.theme,
            ),
        )

    def to_experience_input(self, deck_id: str) -> TarotExperienceInput:
        """Apply caller-provided deck context; v2 Tool JSON stays deck-free."""
        return TarotExperienceInput(
            deck_id=deck_id,
            spread=self.spread.spread_type.value,
            cards=self.spread.cards,
            fortune_context=self.fortune_context,
        )


class StarpathToolContractDispatcher:
    """Choose v1 record parsing or v2 multi-card mapping by contract version.

    The dispatcher consumes result JSON only.  It performs no asset resolution,
    delivery, platform work, or Tool production.
    """

    def __init__(
        self,
        v1_parser: StarpathToolResultParser,
        v2_parser: FutureStarpathToolV2Parser | None = None,
    ) -> None:
        self._v1_parser = v1_parser
        self._v2_parser = v2_parser or FutureStarpathToolV2Parser()

    def parse(self, raw: str) -> StarpathRecord | V2TarotExperiencePayload:
        """Return the established v1 record or a deck-free v2 Experience payload."""
        value = self._decode(raw)
        version = self._contract_version(value)
        if version == STARPATH_TOOL_V1:
            return self._v1_parser.parse(raw)
        if version == FUTURE_STARPATH_TOOL_V2:
            try:
                result = self._v2_parser.parse(value)
                return V2TarotExperiencePayload.from_contract(result)
            except (FutureStarpathToolContractError, ValueError) as error:
                raise StarpathToolContractDispatchError(
                    f"Invalid {FUTURE_STARPATH_TOOL_V2} result"
                ) from error
        raise StarpathToolContractDispatchError(
            f"Unsupported Starpath Tool contract version: {version}"
        )

    @staticmethod
    def _decode(raw: str) -> Mapping[str, object]:
        if not isinstance(raw, str):
            raise StarpathToolContractDispatchError("Expected JSON text")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise StarpathToolContractDispatchError("Invalid JSON") from error
        if not isinstance(value, Mapping):
            raise StarpathToolContractDispatchError("Expected JSON object")
        return value

    @staticmethod
    def _contract_version(value: Mapping[str, object]) -> str:
        metadata = value.get("metadata")
        if not isinstance(metadata, Mapping):
            raise StarpathToolContractDispatchError("Tool result requires metadata object")
        version = metadata.get("contract_version")
        if not isinstance(version, str) or not version.strip():
            raise StarpathToolContractDispatchError(
                "Tool result requires metadata.contract_version"
            )
        return version
