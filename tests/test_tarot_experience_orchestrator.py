"""Tests for the platform-neutral single-card Tarot experience orchestrator."""

from __future__ import annotations

import ast
import inspect
import json
from datetime import datetime, timezone

import pytest
from starpath_plugin.adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards
from starpath_plugin.core.resolver import (
    AssetNotFoundError,
    AssetReference,
    AssetResolver,
    DeckNotFoundError,
)
from starpath_plugin.experience import tarot
from starpath_plugin.experience.asset_consumer import DefaultAssetReferenceConsumer
from starpath_plugin.experience.tarot import (
    ExperienceInputError,
    FortuneContext,
    TarotCardSelection,
    TarotExperienceInput,
    TarotExperienceOrchestrator,
)


class RecordingResolver(AssetResolver):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        self.calls.append((deck_id, card_id))
        if deck_id == "missing_deck":
            raise DeckNotFoundError(deck_id)
        if card_id == "missing_card":
            raise AssetNotFoundError(deck_id, card_id)
        return AssetReference(
            deck_id=deck_id,
            card_id=card_id,
            asset_key=f"{deck_id}_{card_id}",
            path="major/00_the_fool.png",
            format="png",
            version="1.0",
        )


def build_input(
    *, deck_id: str = "a_visual_deck", card_id: str = "major-00"
) -> TarotExperienceInput:
    return TarotExperienceInput(
        deck_id=deck_id,
        spread="single",
        cards=(TarotCardSelection(card_id=card_id, position="main"),),
        fortune_context=FortuneContext(
            quote_id="quote-1",
            text="A cultural symbolic reference.",
            theme="reflection",
        ),
    )


def test_single_card_input_builds_a_platform_neutral_experience_result() -> None:
    resolver = RecordingResolver()
    result = TarotExperienceOrchestrator(resolver, DefaultAssetReferenceConsumer()).build(
        build_input()
    )

    assert result.spread == "single"
    assert result.cards[0].card_id == "major-00"
    assert result.display_resources[0].metadata["card_id"] == "major-00"
    assert result.text_sections[0].section_id == "tarot"
    assert result.text_sections[1].content == "A cultural symbolic reference."
    assert resolver.calls == [("a_visual_deck", "major-00")]


def test_unknown_card_and_deck_keep_existing_resolver_errors() -> None:
    orchestrator = TarotExperienceOrchestrator(
        RecordingResolver(), DefaultAssetReferenceConsumer()
    )

    with pytest.raises(AssetNotFoundError):
        orchestrator.build(build_input(card_id="missing_card"))
    with pytest.raises(DeckNotFoundError):
        orchestrator.build(build_input(deck_id="missing_deck"))


def test_mvp_validates_single_spread_while_model_retains_multiple_card_shape() -> None:
    multi_card = TarotExperienceInput(
        deck_id="a_visual_deck",
        spread="three_card",
        cards=(
            TarotCardSelection(card_id="major-00", position="past"),
            TarotCardSelection(card_id="major-01", position="present"),
        ),
    )

    assert [selection.position for selection in multi_card.cards] == ["past", "present"]
    with pytest.raises(ExperienceInputError):
        TarotExperienceOrchestrator(
            RecordingResolver(), DefaultAssetReferenceConsumer()
        ).build(multi_card)


def test_orchestrator_has_no_message_or_astrbot_dependencies() -> None:
    tree = ast.parse(inspect.getsource(tarot))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "event",
            "send",
            "send_message",
            "chain_result",
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
async def test_existing_tool_contract_remains_without_visual_transport_fields() -> None:
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    adapter = StarpathToolAdapter(
        service,
        now=lambda: datetime(2026, 8, 22, 9, 30, tzinfo=timezone.utc),
    )
    payload = json.loads(await adapter.generate(Event()))

    assert payload["metadata"]["contract_version"] == "starpath.tool.v1"
    assert {"image_path", "image_url", "asset_key", "resolved_path"}.isdisjoint(payload)
