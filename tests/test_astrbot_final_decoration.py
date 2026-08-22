"""Tests for append-only non-streaming AstrBot forward-message decoration."""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path

from starpath_plugin.adapter.astrbot_final_decoration import (
    DECORATION_STATUS_EXTRA_KEY,
    PRESENTATION_CONSUMED_EXTRA_KEY,
    PRESENTATION_EXTRA_KEY,
    AstrBotFinalDecoration,
)
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.presentation import (
    ImagePresentation,
    PresentationResult,
    TextPresentation,
)


class ResultContentType(Enum):
    GENERAL_RESULT = auto()
    STREAMING_FINISH = auto()


class Result:
    def __init__(self, content_type=ResultContentType.GENERAL_RESULT) -> None:
        self.chain = ["native-agent-text"]
        self.result_content_type = content_type


class Event:
    def __init__(self, presentation, result=None) -> None:
        self.extras = {} if presentation is None else {PRESENTATION_EXTRA_KEY: presentation}
        self.result = result or Result()

    def get_extra(self, key, default=None):
        return self.extras.get(key, default)

    def set_extra(self, key, value) -> None:
        self.extras[key] = value

    def get_result(self):
        return self.result


class ForwardRuntime:
    def __init__(self, fail=False) -> None:
        self.fail = fail
        self.payloads = []

    def build_nodes(self, event, payload):
        if self.fail:
            raise RuntimeError("node failure")
        self.payloads.append(payload)
        return ("nodes", payload)


def presentation(*, three_card=False, with_image=True):
    sections = [TextPresentation("title", "Title", "Tarot experience")]
    if with_image:
        sections.append(
            ImagePresentation(DisplayResource("image", "major/00_the_fool.png", "png", {
                "deck_id": "dark_cosmic_archive", "card_id": "major-00"}))
        )
    if three_card:
        sections.extend((
            TextPresentation("tarot_past", "Past", "The Fool"),
            TextPresentation("tarot_present", "Present", "The Magician"),
            TextPresentation("tarot_future", "Future", "The High Priestess"),
        ))
    return PresentationResult("Tarot experience", "quick", tuple(sections))


def decorator(runtime=None):
    root = Path(__file__).resolve().parents[1] / "assets" / "tarot"
    return AstrBotFinalDecoration(root, forward_runtime=runtime or ForwardRuntime())


def test_single_presentation_appends_one_forward_component() -> None:
    runtime = ForwardRuntime()
    event = Event(presentation())
    decorator(runtime).decorate(event)
    assert event.result.chain[0] == "native-agent-text"
    assert event.result.chain[1][0] == "nodes"
    assert [node.node_type for node in runtime.payloads[0].nodes] == ["text", "resource"]
    assert event.extras[PRESENTATION_CONSUMED_EXTRA_KEY] is True
    assert event.extras[DECORATION_STATUS_EXTRA_KEY] == "attached"


def test_three_card_and_text_only_payloads_preserve_order() -> None:
    runtime = ForwardRuntime()
    event = Event(presentation(three_card=True, with_image=False))
    decorator(runtime).decorate(event)
    assert [node.text for node in runtime.payloads[0].nodes] == [
        "Tarot experience", "Past\nThe Fool", "Present\nThe Magician", "Future\nThe High Priestess"
    ]


def test_duplicate_streaming_and_failure_preserve_agent_text() -> None:
    event = Event(presentation())
    d = decorator()
    d.decorate(event)
    d.decorate(event)
    assert len(event.result.chain) == 2

    streaming = Event(presentation(), Result(ResultContentType.STREAMING_FINISH))
    decorator().decorate(streaming)
    assert streaming.result.chain == ["native-agent-text"]
    assert streaming.extras[DECORATION_STATUS_EXTRA_KEY] == "skipped_streaming"

    failed = Event(presentation())
    decorator(ForwardRuntime(fail=True)).decorate(failed)
    assert failed.result.chain == ["native-agent-text"]
    assert failed.extras[DECORATION_STATUS_EXTRA_KEY] == "failed"
