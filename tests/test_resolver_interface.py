from __future__ import annotations

import inspect
from dataclasses import fields

import pytest
from starpath_plugin.core.resolver import (
    AssetNotFoundError,
    AssetReference,
    AssetResolver,
    DeckMetadata,
    DeckNotFoundError,
    DeckResolver,
    InvalidAssetReferenceError,
    interface,
    models,
)


def test_resolver_interfaces_are_abstract_and_deck_agnostic() -> None:
    assert inspect.isabstract(DeckResolver)
    assert inspect.isabstract(AssetResolver)
    assert set(DeckResolver.__abstractmethods__) == {"get_deck"}
    assert set(AssetResolver.__abstractmethods__) == {"resolve"}


def test_asset_reference_has_the_required_metadata_fields() -> None:
    reference = AssetReference(
        deck_id="dark_cosmic_archive",
        card_id="cups_05_five",
        asset_key="dark_cosmic_cups_05_v1",
        path="minor/cups/cups_05_five.png",
        format="png",
        version="1.0.0",
        resolution="1024x1536",
    )

    assert [field.name for field in fields(AssetReference)] == [
        "deck_id",
        "card_id",
        "asset_key",
        "path",
        "format",
        "version",
        "resolution",
    ]
    assert reference.path == "minor/cups/cups_05_five.png"


def test_deck_metadata_has_the_required_fields() -> None:
    metadata = DeckMetadata(
        deck_id="dark_cosmic_archive",
        name="Dark Cosmic Archive",
        version="1.0.0",
        status="approved",
    )

    assert [field.name for field in fields(DeckMetadata)] == [
        "deck_id",
        "name",
        "version",
        "status",
    ]
    assert metadata.status == "approved"


@pytest.mark.parametrize("path", ["", "/assets/card.png", "minor/../card.png", "minor\\card.png"])
def test_asset_reference_rejects_invalid_package_paths(path: str) -> None:
    with pytest.raises(InvalidAssetReferenceError):
        AssetReference(
            deck_id="dark_cosmic_archive",
            card_id="major_17_star",
            asset_key="dark_cosmic_major_17_v1",
            path=path,
            format="png",
        )


def test_resolver_errors_preserve_the_missing_identity() -> None:
    deck_error = DeckNotFoundError("nebula_dream")
    asset_error = AssetNotFoundError("dark_cosmic_archive", "major_17_star")

    assert deck_error.deck_id == "nebula_dream"
    assert asset_error.deck_id == "dark_cosmic_archive"
    assert asset_error.card_id == "major_17_star"


def test_resolver_contract_has_no_io_or_messaging_dependencies() -> None:
    source = inspect.getsource(interface).lower() + inspect.getsource(models).lower()

    for forbidden_term in ("json", "open(", "send_message", "llm", "chat history"):
        assert forbidden_term not in source
