from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest
from starpath_plugin.core.manifest import (
    AssetEntry,
    DeckManifest,
    DeckManifestProvider,
    ManifestNotFoundError,
)
from starpath_plugin.core.manifest.providers import JSONManifestProvider
from starpath_plugin.core.resolver import (
    AssetNotFoundError,
    AssetReference,
    DeckNotFoundError,
    DefaultAssetResolver,
    InvalidAssetReferenceError,
    default_resolver,
)

ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets" / "tarot"


class StaticManifestProvider(DeckManifestProvider):
    def __init__(self, manifest: DeckManifest | None = None) -> None:
        self.manifest = manifest
        self.calls: list[str] = []

    def get_manifest(self, deck_id: str) -> DeckManifest:
        self.calls.append(deck_id)
        if self.manifest is None:
            raise ManifestNotFoundError(deck_id)
        return self.manifest


def build_manifest(*entries: AssetEntry) -> DeckManifest:
    return DeckManifest(
        deck_id="test_deck",
        name="Test Deck",
        version="1.0.0",
        status="approved",
        assets=entries,
    )


def test_default_resolver_maps_a_major_card_from_an_injected_provider() -> None:
    provider = StaticManifestProvider(
        build_manifest(
            AssetEntry(
                card_id="major_17_star",
                asset_key="test_major_17_star_v1",
                path="major/17_the_star.png",
                format="png",
            )
        )
    )

    reference = DefaultAssetResolver(provider).resolve("test_deck", "major_17_star")

    assert isinstance(reference, AssetReference)
    assert reference.deck_id == "test_deck"
    assert reference.card_id == "major_17_star"
    assert reference.asset_key == "test_major_17_star_v1"
    assert reference.version == "1.0.0"
    assert provider.calls == ["test_deck"]


def test_default_resolver_maps_a_real_minor_card() -> None:
    resolver = DefaultAssetResolver(JSONManifestProvider(ASSET_ROOT))

    reference = resolver.resolve("dark_cosmic_archive", "cups_05_five")

    assert reference.path == "minor/cups/cups_05_five.png"
    assert reference.format == "png"
    assert reference.deck_id == "dark_cosmic_archive"


def test_default_resolver_raises_for_an_unknown_card() -> None:
    resolver = DefaultAssetResolver(JSONManifestProvider(ASSET_ROOT))

    with pytest.raises(AssetNotFoundError) as error_info:
        resolver.resolve("dark_cosmic_archive", "unknown_card")

    assert error_info.value.deck_id == "dark_cosmic_archive"
    assert error_info.value.card_id == "unknown_card"


def test_default_resolver_translates_a_missing_manifest() -> None:
    resolver = DefaultAssetResolver(StaticManifestProvider())

    with pytest.raises(DeckNotFoundError) as error_info:
        resolver.resolve("unknown_deck", "unknown_card")

    assert error_info.value.deck_id == "unknown_deck"
    assert isinstance(error_info.value.__cause__, ManifestNotFoundError)


@pytest.mark.parametrize(
    "entry",
    [
        AssetEntry("card", "", "major/card.png", "png"),
        AssetEntry("card", "asset", "major/card.jpg", "png"),
        AssetEntry("card", "asset", "major/card.png", "jpg"),
        AssetEntry("card", "asset", "../major/card.png", "png"),
    ],
)
def test_default_resolver_rejects_invalid_asset_entries(entry: AssetEntry) -> None:
    resolver = DefaultAssetResolver(StaticManifestProvider(build_manifest(entry)))

    with pytest.raises(InvalidAssetReferenceError):
        resolver.resolve("test_deck", "card")


def test_default_resolver_resolves_every_formal_dark_cosmic_asset() -> None:
    provider = JSONManifestProvider(ASSET_ROOT)
    manifest = provider.get_manifest("dark_cosmic_archive")
    resolver = DefaultAssetResolver(provider)

    references = [
        resolver.resolve("dark_cosmic_archive", entry.card_id) for entry in manifest.assets
    ]

    assert len(references) == 78
    assert {reference.card_id for reference in references} == {
        entry.card_id for entry in manifest.assets
    }
    assert all(reference.deck_id == "dark_cosmic_archive" for reference in references)


def test_default_resolver_has_no_io_or_display_dependencies() -> None:
    tree = ast.parse(inspect.getsource(default_resolver))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {"open", "send_message", "llm", "read_chat_history", "user_data", "image"}
    )
