"""Tests for the Agent-facing, v2-only spread Tool adapter."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from starpath_plugin.adapter.tool_v2_adapter import StarpathToolV2Adapter
from starpath_plugin.contracts.starpath_tool_v2 import FutureStarpathToolV2Parser
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathToolV2Producer, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards
from starpath_plugin.experience.tool_contract_dispatcher import (
    StarpathToolContractDispatcher,
    V2TarotExperiencePayload,
)
from starpath_plugin.experience.tool_result_parser import StarpathToolResultParser


class Event:
    def get_sender_id(self) -> str:
        return "agent-capability-test"


def _adapter() -> StarpathToolV2Adapter:
    return StarpathToolV2Adapter(
        StarEngine(load_stars()),
        QuoteEngine(load_quotes()),
        StarpathToolV2Producer(TarotEngine(load_tarot_cards())),
        now=lambda: datetime(2026, 8, 22, 9, 30, tzinfo=timezone.utc),
    )


def test_agent_v2_tool_can_generate_a_schema_valid_single_spread() -> None:
    payload = json.loads(asyncio.run(_adapter().generate(Event(), spread="single")))

    assert payload["metadata"]["contract_version"] == "starpath.tool.v2"
    assert payload["tarot"]["spread"] == "single"
    assert [(card["position"], card["order"]) for card in payload["tarot"]["cards"]] == [
        ("main", 0)
    ]
    assert FutureStarpathToolV2Parser().parse(payload).tarot.spread == "single"


def test_agent_v2_tool_can_generate_three_cards_for_the_existing_dispatcher() -> None:
    raw = asyncio.run(_adapter().generate(Event(), spread="three_card"))
    payload = json.loads(raw)
    parsed = StarpathToolContractDispatcher(StarpathToolResultParser()).parse(raw)

    assert payload["tarot"]["spread"] == "three_card"
    assert [(card["position"], card["order"]) for card in payload["tarot"]["cards"]] == [
        ("past", 0),
        ("present", 1),
        ("future", 2),
    ]
    assert isinstance(parsed, V2TarotExperiencePayload)
    assert parsed.spread.spread_type.value == "three_card"


def test_agent_v2_tool_rejects_unknown_spreads_without_a_contract_payload() -> None:
    payload = json.loads(asyncio.run(_adapter().generate(Event(), spread="celtic_cross")))

    assert payload["error"] == "INVALID_PARAMETERS"
    assert "spread" in payload["reason"]
