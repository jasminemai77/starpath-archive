from __future__ import annotations

import json

import pytest
from starpath_plugin.adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards


class Event:
    def __init__(self, sender_id: str | None = "user-42") -> None:
        self.sender_id = sender_id

    def get_sender_id(self) -> str | None:
        return self.sender_id


def build_adapter() -> StarpathToolAdapter:
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    return StarpathToolAdapter(service)


@pytest.mark.asyncio
async def test_adapter_returns_structured_json() -> None:
    payload = json.loads(await build_adapter().generate(Event()))

    assert set(payload) == {"record_id", "star", "tarot", "quote"}
    assert payload["star"]["id"]
    assert payload["tarot"]["orientation"] in {"upright", "reversed"}


@pytest.mark.asyncio
async def test_adapter_returns_structured_parameter_error() -> None:
    payload = json.loads(await build_adapter().generate(Event(), mode="weekly"))

    assert payload["error"] == "INVALID_PARAMETERS"


@pytest.mark.asyncio
async def test_adapter_needs_only_a_sender_identifier() -> None:
    payload = json.loads(await build_adapter().generate(Event(None)))

    assert payload["error"] == "INVALID_PARAMETERS"
