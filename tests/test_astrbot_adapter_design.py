from __future__ import annotations

import ast
import inspect
from dataclasses import fields

import pytest
from starpath_plugin.adapter import astrbot_platform
from starpath_plugin.adapter.astrbot_platform import (
    AstrBotAdapter,
    AstrBotImagePayload,
    AstrBotPayloadBuildError,
    InvalidPlatformPayloadError,
    UnsupportedAstrBotResourceError,
)
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.platform_adapter import (
    AdapterConversionError,
    PlatformAdapter,
    PlatformPayload,
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


def test_astrbot_adapter_implements_the_generic_platform_contract() -> None:
    assert issubclass(AstrBotAdapter, PlatformAdapter)
    assert not inspect.isabstract(AstrBotAdapter)


def test_astrbot_adapter_converts_display_resource_without_sending() -> None:
    payload = AstrBotAdapter().adapt(build_resource())

    assert isinstance(payload, PlatformPayload)
    assert payload.payload_type == "image"
    assert payload.content == "major/17_the_star.png"
    assert payload.metadata["target_platform"] == "astrbot"


def test_astrbot_image_payload_has_the_declared_fields() -> None:
    payload = AstrBotImagePayload.from_display_resource(build_resource())

    assert [field.name for field in fields(AstrBotImagePayload)] == [
        "type",
        "resource",
        "metadata",
    ]
    assert payload.type == "image"
    assert payload.resource == "major/17_the_star.png"


def test_astrbot_adapter_has_explicit_error_types() -> None:
    with pytest.raises(InvalidPlatformPayloadError):
        AstrBotImagePayload.from_display_resource(None)
    with pytest.raises(InvalidPlatformPayloadError):
        AstrBotImagePayload.from_display_resource(build_resource(path=""))
    with pytest.raises(UnsupportedAstrBotResourceError):
        AstrBotImagePayload.from_display_resource(build_resource(resource_type="video"))

    assert issubclass(AstrBotPayloadBuildError, AdapterConversionError)
    assert issubclass(InvalidPlatformPayloadError, AdapterConversionError)


def test_astrbot_adapter_design_has_no_runtime_or_send_dependencies() -> None:
    tree = ast.parse(inspect.getsource(astrbot_platform))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {"open", "send", "send_message", "llm", "read_chat_history", "user_data", "context"}
    )
