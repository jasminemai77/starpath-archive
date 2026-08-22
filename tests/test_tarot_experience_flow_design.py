"""Contract checks that preserve the frozen Tarot experience-flow boundaries."""

from __future__ import annotations

import ast
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from starpath_plugin.adapter.tool_adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.manifest.providers import JSONManifestProvider
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards
from starpath_plugin.core.resolver import DefaultAssetResolver, default_resolver
from starpath_plugin.experience import asset_consumer, record
from starpath_plugin.experience.asset_consumer import DefaultAssetReferenceConsumer

ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets" / "tarot"


class Event:
    def get_sender_id(self) -> str:
        return "experience-flow-test"


def build_adapter() -> StarpathToolAdapter:
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    return StarpathToolAdapter(
        service,
        now=lambda: datetime(2026, 8, 22, 9, 30, tzinfo=timezone.utc),
    )


def walk_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(walk_keys(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(walk_keys(item) for item in value))
    return set()


@pytest.mark.asyncio
async def test_tool_contract_exposes_logical_tarot_identity_without_image_fields() -> None:
    payload = json.loads(await build_adapter().generate(Event()))

    assert payload["tarot"]["id"]
    assert {"image_path", "image_url", "asset_key", "resolved_path"}.isdisjoint(
        walk_keys(payload)
    )


def test_experience_can_consume_resolved_card_identity_without_sending() -> None:
    provider = JSONManifestProvider(ASSET_ROOT)
    manifest = provider.get_manifest("dark_cosmic_archive")
    reference = DefaultAssetResolver(provider).resolve(
        manifest.deck_id, manifest.assets[0].card_id
    )

    display = DefaultAssetReferenceConsumer().consume(reference)

    assert display.metadata["card_id"] == reference.card_id
    assert display.path == reference.path


def test_multiple_card_selections_share_the_same_deck_agnostic_resolution_path() -> None:
    provider = JSONManifestProvider(ASSET_ROOT)
    manifest = provider.get_manifest("dark_cosmic_archive")
    resolver = DefaultAssetResolver(provider)
    consumer = DefaultAssetReferenceConsumer()
    selected_cards = manifest.assets[:3]

    displays = [
        consumer.consume(resolver.resolve(manifest.deck_id, selected.card_id))
        for selected in selected_cards
    ]

    assert [display.metadata["card_id"] for display in displays] == [
        selected.card_id for selected in selected_cards
    ]


def test_experience_and_resolver_remain_free_of_send_and_astrbot_dependencies() -> None:
    source = "\n".join(
        (
            inspect.getsource(record),
            inspect.getsource(asset_consumer),
            inspect.getsource(default_resolver),
        )
    )
    tree = ast.parse(source)
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {"send", "send_message", "chain_result", "astrbot", "event"}
    )
