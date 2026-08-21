from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields

import pytest
from starpath_plugin.core.manifest import (
    AssetEntry,
    DeckManifest,
    DeckManifestProvider,
    InvalidManifestError,
    ManifestNotFoundError,
    interface,
    models,
)


def build_manifest() -> DeckManifest:
    return DeckManifest(
        deck_id="dark_cosmic_archive",
        name="Dark Cosmic Archive",
        version="1.0.0",
        status="approved",
        assets=(
            AssetEntry(
                card_id="major_17_star",
                asset_key="dark_cosmic_major_17_v1",
                path="major/17_the_star.png",
                format="png",
            ),
        ),
    )


def test_manifest_provider_interface_is_abstract() -> None:
    assert inspect.isabstract(DeckManifestProvider)
    assert set(DeckManifestProvider.__abstractmethods__) == {"get_manifest"}


def test_deck_manifest_has_the_required_immutable_fields() -> None:
    manifest = build_manifest()

    assert [field.name for field in fields(DeckManifest)] == [
        "deck_id",
        "name",
        "version",
        "status",
        "assets",
    ]
    assert isinstance(manifest.assets, tuple)
    with pytest.raises(FrozenInstanceError):
        manifest.status = "disabled"  # type: ignore[misc]


def test_asset_entry_has_the_required_immutable_fields() -> None:
    entry = build_manifest().assets[0]

    assert [field.name for field in fields(AssetEntry)] == [
        "card_id",
        "asset_key",
        "path",
        "format",
    ]
    with pytest.raises(FrozenInstanceError):
        entry.path = "other.png"  # type: ignore[misc]


def test_manifest_errors_preserve_a_locatable_deck_identity() -> None:
    error = ManifestNotFoundError("nebula_dream")

    assert error.deck_id == "nebula_dream"
    assert "nebula_dream" in str(error)
    assert issubclass(InvalidManifestError, Exception)


def test_manifest_provider_contract_has_no_io_or_messaging_dependencies() -> None:
    source = inspect.getsource(interface).lower() + inspect.getsource(models).lower()

    for forbidden_term in ("json", "open(", "send_message", "llm", "chat history"):
        assert forbidden_term not in source
