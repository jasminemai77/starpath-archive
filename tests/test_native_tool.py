from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path

import pytest


def _install_astrbot_stubs(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    registry: dict[str, object] = {}
    astrbot = types.ModuleType("astrbot")
    api = types.ModuleType("astrbot.api")
    event = types.ModuleType("astrbot.api.event")
    star = types.ModuleType("astrbot.api.star")

    def llm_tool(*, name: str):
        def decorate(function):
            registry[name] = function
            function.tool_name = name
            return function

        return decorate

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
    return registry


def test_plugin_loads_and_registers_native_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _install_astrbot_stubs(monkeypatch)
    main = importlib.import_module("starpath_plugin.main")

    assert main.StarpathArchivePlugin
    assert registry["generate_starpath_record"].__name__ == "generate_starpath_record"


@pytest.mark.asyncio
async def test_native_tool_delegates_to_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_astrbot_stubs(monkeypatch)
    main = importlib.import_module("starpath_plugin.main")

    class Adapter:
        async def generate(self, event, mode, spread):
            assert event == "event"
            assert (mode, spread) == ("daily", "single")
            return json.dumps({"record_id": "starpath-test"})

    plugin = object.__new__(main.StarpathArchivePlugin)
    plugin._adapter = Adapter()
    assert json.loads(await plugin.generate_starpath_record("event")) == {
        "record_id": "starpath-test"
    }


def test_entrypoint_has_no_disallowed_agent_or_message_boundaries() -> None:
    package_root = Path(importlib.import_module("starpath_plugin").__path__[0])
    content = (package_root / "main.py").read_text(encoding="utf-8")

    for forbidden in ("event.send(", "llm_generate(", "create_task(", "@filter.command"):
        assert forbidden not in content
