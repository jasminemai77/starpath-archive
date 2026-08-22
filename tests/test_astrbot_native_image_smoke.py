"""Tests for the one-off native AstrBot image smoke preparation chain."""

from __future__ import annotations

import ast
import inspect
import sys
import types
from pathlib import Path

from starpath_plugin.adapter import astrbot_native_image, astrbot_native_image_smoke
from starpath_plugin.adapter.astrbot_native_image import build_native_smoke_chain
from starpath_plugin.adapter.astrbot_native_image_smoke import (
    SMOKE_DEFAULT_DECK_ID,
    build_native_image_smoke_service,
)


def test_native_image_smoke_follows_the_real_manifest_to_prepared_png_chain() -> None:
    service = build_native_image_smoke_service()
    manifest = service._manifest_provider.get_manifest(SMOKE_DEFAULT_DECK_ID)

    preparation = service.prepare()

    assert preparation.asset_reference.card_id == manifest.assets[0].card_id
    assert preparation.asset_reference.path == manifest.assets[0].path
    assert preparation.display_resource.path == preparation.asset_reference.path
    assert preparation.payload.resource == preparation.asset_reference.path
    assert Path(preparation.prepared_resource.resolved_path).is_file()
    assert preparation.prepared_resource.resolved_path.endswith(".png")


def test_native_image_smoke_builds_astrbot_components_from_prepared_path(monkeypatch) -> None:
    calls: list[str] = []
    components = types.ModuleType("astrbot.api.message_components")

    class Plain:
        def __init__(self, text: str) -> None:
            self.text = text

    class Image:
        @staticmethod
        def fromFileSystem(path: str) -> tuple[str, str]:
            calls.append(path)
            return ("image", path)

    components.Plain = Plain
    components.Image = Image
    api = types.ModuleType("astrbot.api")
    api.message_components = components
    astrbot = types.ModuleType("astrbot")
    astrbot.api = api
    monkeypatch.setitem(sys.modules, "astrbot", astrbot)
    monkeypatch.setitem(sys.modules, "astrbot.api", api)
    monkeypatch.setitem(sys.modules, "astrbot.api.message_components", components)

    preparation = build_native_image_smoke_service().prepare()
    chain = build_native_smoke_chain(preparation.prepared_resource)

    assert chain[0].text.startswith("[DEV]")
    assert chain[1] == ("image", preparation.prepared_resource.resolved_path)
    assert calls == [preparation.prepared_resource.resolved_path]


def test_native_image_smoke_has_no_direct_platform_transport_or_encoding() -> None:
    source = inspect.getsource(astrbot_native_image) + inspect.getsource(
        astrbot_native_image_smoke
    )
    tree = ast.parse(source)
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "onebot",
            "napcat",
            "aiocqhttp",
            "base64",
            "send_group_msg",
            "send_private_msg",
            "websocket",
        }
    )
