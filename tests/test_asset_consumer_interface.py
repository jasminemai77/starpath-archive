from __future__ import annotations

import ast
import inspect
from dataclasses import fields

import pytest
from starpath_plugin.core.resolver import AssetReference
from starpath_plugin.experience import asset_consumer
from starpath_plugin.experience.asset_consumer import (
    AssetReferenceConsumer,
    AssetReferenceMissingError,
    DisplayResource,
    UnsupportedDisplayResourceError,
)


def build_reference(*, format: str = "png") -> AssetReference:
    return AssetReference(
        deck_id="dark_cosmic_archive",
        card_id="cups_05_five",
        asset_key="dark_cosmic_cups_05_v1",
        path="minor/cups/cups_05_five.png",
        format=format,
        version="1.0.0",
        resolution="1024x1536",
    )


def test_asset_reference_consumer_is_an_abstract_contract() -> None:
    assert inspect.isabstract(AssetReferenceConsumer)
    assert set(AssetReferenceConsumer.__abstractmethods__) == {"consume"}


def test_asset_reference_converts_to_a_platform_neutral_display_resource() -> None:
    display_resource = DisplayResource.from_asset_reference(build_reference())

    assert display_resource.resource_type == "image"
    assert display_resource.path == "minor/cups/cups_05_five.png"
    assert display_resource.format == "png"
    assert display_resource.metadata == {
        "deck_id": "dark_cosmic_archive",
        "card_id": "cups_05_five",
        "asset_key": "dark_cosmic_cups_05_v1",
        "version": "1.0.0",
        "resolution": "1024x1536",
    }


def test_display_resource_has_the_declared_fields() -> None:
    assert [field.name for field in fields(DisplayResource)] == [
        "resource_type",
        "path",
        "format",
        "metadata",
    ]


def test_display_conversion_rejects_missing_or_unsupported_assets() -> None:
    with pytest.raises(AssetReferenceMissingError):
        DisplayResource.from_asset_reference(None)
    with pytest.raises(UnsupportedDisplayResourceError):
        DisplayResource.from_asset_reference(build_reference(format="jpg"))


def test_asset_consumer_contract_has_no_platform_or_message_dependencies() -> None:
    tree = ast.parse(inspect.getsource(asset_consumer))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {"open", "send_message", "llm", "read_chat_history", "user_data", "qq", "telegram"}
    )
