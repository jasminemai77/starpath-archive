from __future__ import annotations

import ast
import inspect
from collections import Counter
from pathlib import Path

import pytest
from starpath_plugin.core.manifest import (
    AssetEntry,
    DeckManifest,
    InvalidManifestError,
    ManifestNotFoundError,
)
from starpath_plugin.core.manifest.providers import JSONManifestProvider, json_provider

ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets" / "tarot"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "manifest_provider"


def test_json_provider_loads_the_real_dark_cosmic_manifest() -> None:
    manifest = JSONManifestProvider(ASSET_ROOT).get_manifest("dark_cosmic_archive")

    assert isinstance(manifest, DeckManifest)
    assert manifest.deck_id == "dark_cosmic_archive"
    assert manifest.name == "Dark Cosmic Archive"
    assert manifest.version == "1.0"


def test_json_provider_preserves_the_complete_78_asset_inventory() -> None:
    manifest = JSONManifestProvider(ASSET_ROOT).get_manifest("dark_cosmic_archive")
    groups = Counter(
        entry.path.split("/")[1] if entry.path.startswith("minor/") else "major"
        for entry in manifest.assets
    )

    assert len(manifest.assets) == 78
    assert groups == {"major": 22, "wands": 14, "cups": 14, "swords": 14, "pentacles": 14}


def test_json_provider_converts_every_entry_to_the_required_contract() -> None:
    manifest = JSONManifestProvider(ASSET_ROOT).get_manifest("dark_cosmic_archive")

    assert all(isinstance(entry, AssetEntry) for entry in manifest.assets)
    assert all(
        entry.card_id and entry.asset_key and entry.path and entry.format == "png"
        for entry in manifest.assets
    )
    assert any(entry.card_id == "major-17" and entry.asset_key for entry in manifest.assets)


def test_json_provider_raises_not_found_for_a_missing_manifest() -> None:
    with pytest.raises(ManifestNotFoundError):
        JSONManifestProvider(FIXTURE_ROOT).get_manifest("missing_deck")


@pytest.mark.parametrize(
    "deck_id",
    [
        "missing_fields",
        "unsafe_path",
    ],
)
def test_json_provider_rejects_missing_fields_and_unsafe_paths(deck_id: str) -> None:
    with pytest.raises(InvalidManifestError):
        JSONManifestProvider(FIXTURE_ROOT).get_manifest(deck_id)


def test_json_provider_rejects_invalid_json() -> None:
    with pytest.raises(InvalidManifestError):
        JSONManifestProvider(FIXTURE_ROOT).get_manifest("invalid_json")


def test_json_provider_has_no_messaging_or_model_dependencies() -> None:
    source = inspect.getsource(json_provider).lower()
    tree = ast.parse(source)
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint({"send_message", "llm", "read_chat_history", "user_data"})
