"""Tests for pure StarpathRecord to TarotExperienceInput conversion."""

from __future__ import annotations

import ast
import inspect
import json
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest
from starpath_plugin.adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards
from starpath_plugin.experience import record_adapter
from starpath_plugin.experience.record_adapter import (
    InvalidStarpathRecordError,
    MissingDeckContextError,
    MissingTarotCardError,
    StarpathRecordExperienceAdapter,
)


def build_record():
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    return service.generate(
        user_hash="record-adapter-test",
        on_date=date(2026, 8, 22),
        mode="daily",
        spread="single",
    )


def test_adapter_maps_real_single_card_record_to_explicit_deck_input() -> None:
    record = build_record()

    experience_input = StarpathRecordExperienceAdapter().adapt(
        record,
        deck_id="a_visual_deck",
        spread="single",
    )

    assert experience_input.deck_id == "a_visual_deck"
    assert experience_input.spread == "single"
    assert experience_input.cards[0].card_id == record.tarot.card.id
    assert experience_input.cards[0].position == "main"
    assert experience_input.fortune_context is not None
    assert experience_input.fortune_context.quote_id == record.quote.id
    assert experience_input.fortune_context.text == record.quote.text
    assert experience_input.fortune_context.theme == record.quote.theme


def test_adapter_rejects_invalid_record_missing_card_and_missing_deck_context() -> None:
    adapter = StarpathRecordExperienceAdapter()
    record = build_record()
    empty_card = replace(record.tarot.card, id="")
    missing_card_record = replace(record, tarot=replace(record.tarot, card=empty_card))

    with pytest.raises(InvalidStarpathRecordError):
        adapter.adapt(object(), deck_id="a_visual_deck")  # type: ignore[arg-type]
    with pytest.raises(MissingTarotCardError):
        adapter.adapt(missing_card_record, deck_id="a_visual_deck")
    with pytest.raises(MissingDeckContextError):
        adapter.adapt(record, deck_id="")


def test_adapter_does_not_depend_on_resolver_or_platform_boundaries() -> None:
    tree = ast.parse(inspect.getsource(record_adapter))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "resolve",
            "event",
            "send",
            "send_message",
            "messagechain",
            "astrbot",
            "onebot",
            "napcat",
            "llm",
            "user_data",
        }
    )


class Event:
    def get_sender_id(self) -> str:
        return "tool-contract-test"


@pytest.mark.asyncio
async def test_adapter_does_not_change_existing_tool_contract() -> None:
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    tool = StarpathToolAdapter(
        service,
        now=lambda: datetime(2026, 8, 22, 9, 30, tzinfo=timezone.utc),
    )

    payload = json.loads(await tool.generate(Event()))

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
    assert {"image_path", "image_url", "asset_key", "display_resources"}.isdisjoint(
        payload
    )
