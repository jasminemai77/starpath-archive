from __future__ import annotations

import ast
import inspect
from dataclasses import fields
from pathlib import Path

import pytest
from starpath_plugin.adapter.astrbot_platform import AstrBotImagePayload
from starpath_plugin.experience.delivery import (
    InvalidRuntimeResourceError,
    LocalRuntimeImageDelivery,
    PreparedAstrBotResource,
    RuntimeImageDelivery,
    RuntimePayloadPreparationError,
    RuntimeResourceNotFoundError,
    local,
)

ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets" / "tarot" / "dark_cosmic_archive"


def build_payload(resource: str = "major/17_the_star.png") -> AstrBotImagePayload:
    return AstrBotImagePayload(
        type="image",
        resource=resource,
        metadata={"deck_id": "dark_cosmic_archive", "card_id": "major-17"},
    )


def test_runtime_delivery_interface_is_abstract() -> None:
    assert inspect.isabstract(RuntimeImageDelivery)
    assert set(RuntimeImageDelivery.__abstractmethods__) == {"prepare"}


def test_local_runtime_delivery_prepares_a_formal_image_without_reading_it() -> None:
    prepared = LocalRuntimeImageDelivery(ASSET_ROOT).prepare(build_payload())

    assert isinstance(prepared, PreparedAstrBotResource)
    assert Path(prepared.resolved_path).is_file()
    assert prepared.resource_type == "image"
    assert prepared.media_type == "image/png"
    assert prepared.metadata["card_id"] == "major-17"


def test_prepared_resource_has_the_declared_fields() -> None:
    assert [field.name for field in fields(PreparedAstrBotResource)] == [
        "resource_type",
        "resolved_path",
        "media_type",
        "metadata",
    ]


@pytest.mark.parametrize("reference", ["/major/17_the_star.png", "C:\\image.png", "../secret.png"])
def test_local_runtime_delivery_rejects_absolute_and_traversal_paths(reference: str) -> None:
    with pytest.raises(InvalidRuntimeResourceError):
        LocalRuntimeImageDelivery(ASSET_ROOT).prepare(build_payload(reference))


def test_local_runtime_delivery_has_explicit_missing_and_invalid_payload_errors() -> None:
    with pytest.raises(RuntimeResourceNotFoundError):
        LocalRuntimeImageDelivery(ASSET_ROOT).prepare(build_payload("major/missing.png"))
    with pytest.raises(RuntimePayloadPreparationError):
        LocalRuntimeImageDelivery(ASSET_ROOT).prepare(object())  # type: ignore[arg-type]


def test_runtime_delivery_boundary_has_no_send_or_user_dependencies() -> None:
    tree = ast.parse(inspect.getsource(local))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "event",
            "send",
            "send_message",
            "bot",
            "llm",
            "read_chat_history",
            "user_data",
        }
    )
