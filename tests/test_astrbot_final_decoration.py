"""Tests for append-only non-streaming AstrBot final decoration."""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path

from starpath_plugin.adapter.astrbot_final_decoration import (
    DECORATION_STATUS_EXTRA_KEY,
    PRESENTATION_CONSUMED_EXTRA_KEY,
    PRESENTATION_EXTRA_KEY,
    AstrBotFinalDecoration,
)
from starpath_plugin.adapter.astrbot_platform import AstrBotAdapter
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.presentation import ImagePresentation, PresentationResult
from starpath_plugin.experience.presentation_consumer import StructuredPresentationConsumer


class ResultContentType(Enum):
    GENERAL_RESULT = auto()
    STREAMING_FINISH = auto()


class Result:
    def __init__(self, content_type: ResultContentType = ResultContentType.GENERAL_RESULT) -> None:
        self.chain: list[object] = ["native-agent-text"]
        self.result_content_type = content_type


class Event:
    def __init__(
        self,
        presentation: PresentationResult | None,
        result: Result | None = None,
    ) -> None:
        self.extras: dict[str, object] = {}
        if presentation is not None:
            self.extras[PRESENTATION_EXTRA_KEY] = presentation
        self.result = result if result is not None else Result()

    def get_extra(self, key: str, default: object = None) -> object:
        return self.extras.get(key, default)

    def set_extra(self, key: str, value: object) -> None:
        self.extras[key] = value

    def get_result(self) -> Result | None:
        return self.result


def presentation() -> PresentationResult:
    resource = DisplayResource(
        "image",
        "major/00_the_fool.png",
        "png",
        {"deck_id": "dark_cosmic_archive", "card_id": "major-00"},
    )
    return PresentationResult("Tarot experience", "quick", (ImagePresentation(resource),))


def build_decorator(*, fail: bool = False) -> AstrBotFinalDecoration:
    def image_builder(prepared: object) -> object:
        if fail:
            raise RuntimeError("image construction failed")
        return ("image", prepared.resolved_path)  # type: ignore[attr-defined]

    root = Path(__file__).resolve().parents[1] / "assets" / "tarot"
    return AstrBotFinalDecoration(
        StructuredPresentationConsumer(),
        AstrBotAdapter(),
        root,
        image_builder,
    )


def test_non_streaming_presentation_appends_one_image_to_the_existing_text_chain() -> None:
    event = Event(presentation())

    build_decorator().decorate(event)

    assert event.result.chain[0] == "native-agent-text"
    assert event.result.chain[1][0] == "image"
    assert event.result.chain[1][1].endswith("major\\00_the_fool.png")
    assert event.extras[PRESENTATION_CONSUMED_EXTRA_KEY] is True
    assert event.extras[DECORATION_STATUS_EXTRA_KEY] == "attached"


def test_absent_presentation_leaves_the_native_agent_result_unchanged() -> None:
    event = Event(None)

    build_decorator().decorate(event)

    assert event.result.chain == ["native-agent-text"]
    assert PRESENTATION_CONSUMED_EXTRA_KEY not in event.extras


def test_duplicate_decoration_does_not_append_a_second_image() -> None:
    event = Event(presentation())
    decorator = build_decorator()

    decorator.decorate(event)
    decorator.decorate(event)

    assert len(event.result.chain) == 2
    assert event.extras[PRESENTATION_CONSUMED_EXTRA_KEY] is True


def test_streaming_result_skips_image_and_preserves_text() -> None:
    event = Event(presentation(), Result(ResultContentType.STREAMING_FINISH))

    build_decorator().decorate(event)

    assert event.result.chain == ["native-agent-text"]
    assert event.extras[DECORATION_STATUS_EXTRA_KEY] == "skipped_streaming"
    assert PRESENTATION_CONSUMED_EXTRA_KEY not in event.extras


def test_failed_image_construction_preserves_text_and_records_failure() -> None:
    event = Event(presentation())

    build_decorator(fail=True).decorate(event)

    assert event.result.chain == ["native-agent-text"]
    assert event.extras[DECORATION_STATUS_EXTRA_KEY] == "failed"
    assert PRESENTATION_CONSUMED_EXTRA_KEY not in event.extras


def test_final_decoration_contains_no_direct_send_or_tool_contract_dependencies() -> None:
    source = (
        Path(__file__).resolve().parents[1] / "adapter" / "astrbot_final_decoration.py"
    ).read_text(encoding="utf-8").lower()

    for forbidden in ("event.send(", "messagechain", "generate_starpath_record", "llm_tool"):
        assert forbidden not in source
