from __future__ import annotations

import ast
import inspect
from dataclasses import fields

import pytest
from starpath_plugin.experience import platform_adapter
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.platform_adapter import (
    AdapterConversionError,
    InvalidDisplayResourceError,
    PlatformAdapter,
    PlatformPayload,
    UnsupportedResourceTypeError,
)


def build_resource(
    *, resource_type: str = "image", path: str = "major/17_the_star.png", format: str = "png"
) -> DisplayResource:
    return DisplayResource(
        resource_type=resource_type,
        path=path,
        format=format,
        metadata={"deck_id": "dark_cosmic_archive", "card_id": "major-17"},
    )


def test_platform_adapter_is_an_abstract_contract() -> None:
    assert inspect.isabstract(PlatformAdapter)
    assert set(PlatformAdapter.__abstractmethods__) == {"adapt"}


def test_display_resource_converts_to_a_generic_platform_payload() -> None:
    payload = PlatformPayload.from_display_resource(build_resource())

    assert payload.payload_type == "image"
    assert payload.content == "major/17_the_star.png"
    assert payload.metadata == {
        "format": "png",
        "deck_id": "dark_cosmic_archive",
        "card_id": "major-17",
    }


def test_platform_payload_has_the_declared_fields() -> None:
    assert [field.name for field in fields(PlatformPayload)] == [
        "payload_type",
        "content",
        "metadata",
    ]


def test_platform_payload_rejects_invalid_or_unsupported_resources() -> None:
    with pytest.raises(InvalidDisplayResourceError):
        PlatformPayload.from_display_resource(None)
    with pytest.raises(InvalidDisplayResourceError):
        PlatformPayload.from_display_resource(build_resource(path=""))
    with pytest.raises(UnsupportedResourceTypeError):
        PlatformPayload.from_display_resource(build_resource(resource_type="video"))

    assert issubclass(InvalidDisplayResourceError, AdapterConversionError)
    assert issubclass(UnsupportedResourceTypeError, AdapterConversionError)


def test_platform_adapter_contract_has_no_send_or_platform_dependencies() -> None:
    tree = ast.parse(inspect.getsource(platform_adapter))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "open",
            "send_message",
            "llm",
            "read_chat_history",
            "user_data",
            "onebot",
            "cqcode",
        }
    )
