"""Mock-only tests for post-tool presentation state capture."""

from __future__ import annotations

import asyncio

from starpath_plugin.experience.post_tool_capture import (
    CAPTURE_STATUS_EXTRA_KEY,
    PRESENTATION_EXTRA_KEY,
    STARPATH_TOOL_NAME,
    StarpathExperienceCaptureHook,
)
from starpath_plugin.experience.presentation import PresentationResult


class Event:
    def __init__(self) -> None:
        self.extras: dict[str, object] = {}

    def set_extra(self, key: str, value: object) -> None:
        self.extras[key] = value

    def get_extra(self, key: str):
        return self.extras.get(key)


class Tool:
    def __init__(self, name: str) -> None:
        self.name = name


class DeckProvider:
    def __init__(self, deck_id: str = "deck") -> None:
        self.deck_id = deck_id

    def get_default_deck_id(self) -> str:
        return self.deck_id


class Application:
    def __init__(self) -> None:
        self.calls = []

    def build(self, record, *, deck_id, spread):
        self.calls.append((record, deck_id, spread))
        return "experience"


class Builder:
    def __init__(self, presentation) -> None:
        self.presentation = presentation
        self.calls = []

    def build(self, experience, *, mode):
        self.calls.append((experience, mode))
        return self.presentation


def test_matching_tool_captures_presentation_once() -> None:
    event, app = Event(), Application()
    presentation = PresentationResult("x", "quick", ())
    builder = Builder(presentation)
    hook = StarpathExperienceCaptureHook(lambda result: "record", app, builder, DeckProvider())

    asyncio.run(hook.capture(event, Tool(STARPATH_TOOL_NAME), {"spread": "single"}, "result"))

    assert app.calls == [("record", "deck", "single")]
    assert builder.calls == [("experience", "quick")]
    assert event.extras[PRESENTATION_EXTRA_KEY] is presentation
    assert event.extras[CAPTURE_STATUS_EXTRA_KEY] == "captured"


def test_non_starpath_or_failure_does_not_interrupt_agent_flow() -> None:
    event = Event()
    def fail(_):
        raise ValueError()

    hook = StarpathExperienceCaptureHook(fail, Application(), Builder(None), DeckProvider())
    asyncio.run(hook.capture(event, Tool("other"), {}, object()))
    assert event.extras == {}
    asyncio.run(hook.capture(event, Tool(STARPATH_TOOL_NAME), {}, object()))
    assert event.extras[CAPTURE_STATUS_EXTRA_KEY] == "failed"
    assert PRESENTATION_EXTRA_KEY not in event.extras
