"""AstrBot boundary simulation without a live AstrBot or QQ connection."""

from __future__ import annotations

import importlib
import json
import sys
import types

import pytest


def _install_astrbot_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    astrbot = types.ModuleType("astrbot")
    api = types.ModuleType("astrbot.api")
    event = types.ModuleType("astrbot.api.event")
    star = types.ModuleType("astrbot.api.star")

    def llm_tool(*, name: str):
        return lambda function: function

    def register(*_args, **_kwargs):
        return lambda cls: cls

    class Filter:
        @staticmethod
        def on_llm_tool_respond():
            return lambda function: function

        @staticmethod
        def on_decorating_result():
            return lambda function: function

    class FrameworkStar:
        def __init__(self, context):
            self.context = context

    api.AstrBotConfig = dict
    api.llm_tool = llm_tool
    api.logger = types.SimpleNamespace(info=lambda _message: None)
    event.AstrMessageEvent = object
    event.filter = Filter
    star.Context = object
    star.Star = FrameworkStar
    star.register = register
    astrbot.api = api
    monkeypatch.setitem(sys.modules, "astrbot", astrbot)
    monkeypatch.setitem(sys.modules, "astrbot.api", api)
    monkeypatch.setitem(sys.modules, "astrbot.api.event", event)
    monkeypatch.setitem(sys.modules, "astrbot.api.star", star)
    sys.modules.pop("starpath_plugin.main", None)


class SimulatedEvent:
    def get_sender_id(self) -> str:
        return "runtime-simulation-user"


@pytest.mark.asyncio
async def test_astrbot_runtime_simulation_returns_the_tool_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_astrbot_stubs(monkeypatch)
    main = importlib.import_module("starpath_plugin.main")
    plugin = main.StarpathArchivePlugin(context=object())

    payload = json.loads(await plugin.generate_starpath_record(SimulatedEvent()))

    assert set(payload) == {
        "record_id",
        "generated_at",
        "mode",
        "spread",
        "star",
        "tarot",
        "quote",
        "metadata",
    }
    assert payload["metadata"]["content_scope"] == "symbolic_entertainment"
