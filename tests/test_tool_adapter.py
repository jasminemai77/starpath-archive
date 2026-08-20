from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from starpath_plugin.adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards


class Event:
    def __init__(self, sender_id: str | None = "user-42") -> None:
        self.sender_id = sender_id

    def get_sender_id(self) -> str | None:
        return self.sender_id


def build_adapter(now=None) -> StarpathToolAdapter:
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    return StarpathToolAdapter(service, now=now)


@pytest.mark.asyncio
async def test_adapter_returns_complete_tool_contract() -> None:
    def fixed_now() -> datetime:
        return datetime(2026, 8, 20, 9, 30, tzinfo=timezone.utc)

    payload = json.loads(await build_adapter(now=fixed_now).generate(Event()))

    assert set(payload) == {
        "record_id",
        "generated_at",
        "mode",
        "spread",
        "star",
        "tarot",
        "quote",
        "metadata",
    }
    assert payload["generated_at"] == "2026-08-20T09:30:00Z"
    assert (payload["mode"], payload["spread"]) == ("daily", "single")
    assert payload["star"]["id"]
    assert payload["tarot"]["orientation"] in {"upright", "reversed"}
    assert payload["metadata"] == {
        "contract_version": "starpath.tool.v1",
        "content_scope": "symbolic_entertainment",
        "generation_timezone": "UTC",
        "experience": {
            "star_type": payload["star"]["type"],
            "tarot_arcana": payload["tarot"]["arcana"],
            "tarot_orientation": payload["tarot"]["orientation"],
            "quote_theme": payload["quote"]["theme"],
        },
    }


@pytest.mark.asyncio
async def test_adapter_returns_structured_parameter_error() -> None:
    payload = json.loads(await build_adapter().generate(Event(), mode="weekly"))

    assert payload["error"] == "INVALID_PARAMETERS"


@pytest.mark.asyncio
async def test_adapter_needs_only_a_sender_identifier() -> None:
    payload = json.loads(await build_adapter().generate(Event(None)))

    assert payload["error"] == "INVALID_PARAMETERS"
