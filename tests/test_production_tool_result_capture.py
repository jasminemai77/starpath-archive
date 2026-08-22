"""Production-boundary tests for capture-only AstrBot tool-result handling."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from starpath_plugin.experience.deck_provider import (
    ConfigDeckProvider,
    MissingDefaultDeckError,
    PackageDeckProvider,
)
from starpath_plugin.experience.post_tool_capture import (
    CAPTURE_STATUS_EXTRA_KEY,
    PRESENTATION_EXTRA_KEY,
    STARPATH_TOOL_NAME,
    StarpathExperienceCaptureHook,
)
from starpath_plugin.experience.presentation import PresentationResult
from starpath_plugin.experience.tool_result_parser import (
    InvalidStarpathToolResultError,
    MissingTarotCardError,
    StarpathToolResultParser,
    ToolResultExtractionError,
    ToolResultExtractor,
)


@dataclass
class TextContent:
    type: str
    text: str


@dataclass
class CallToolResult:
    content: list[object]


class Event:
    def __init__(self) -> None:
        self.extras: dict[str, object] = {}

    def get_extra(self, key: str):
        return self.extras.get(key)

    def set_extra(self, key: str, value: object) -> None:
        self.extras[key] = value


class Tool:
    name = STARPATH_TOOL_NAME


class Application:
    def __init__(self) -> None:
        self.calls: list[tuple[object, str, str]] = []
        self.input_calls: list[object] = []

    def build(self, record: object, *, deck_id: str, spread: str) -> str:
        self.calls.append((record, deck_id, spread))
        return "experience"

    def build_input(self, experience_input: object) -> str:
        self.input_calls.append(experience_input)
        return "experience"


class PresentationBuilder:
    def build(self, experience: str, *, mode: str) -> PresentationResult:
        assert (experience, mode) == ("experience", "quick")
        return PresentationResult("Tarot experience", "quick", ())


def tool_payload() -> dict[str, object]:
    return {
        "record_id": "starpath-capture-test",
        "star": {
            "id": "vega",
            "name": "Vega",
            "zh_name": "织女星",
            "type": "star",
            "astronomy": "A real nearby star.",
            "symbolism": "A cultural celestial symbol.",
        },
        "tarot": {
            "id": "major-00",
            "name": "The Fool",
            "zh_name": "愚者",
            "number": 0,
            "arcana": "major",
            "suit": None,
            "keywords": ["beginnings"],
            "upright_meaning": ["openness"],
            "reversed_meaning": ["hesitation"],
            "symbolism": {"theme": "journey"},
            "literary_material": ["A traveller under stars."],
            "image": None,
            "orientation": "upright",
            "draw_keywords": ["beginnings"],
            "meaning": ["openness"],
        },
        "quote": {"id": "q1", "text": "Look upward.", "theme": "exploration"},
        "metadata": {"contract_version": "starpath.tool.v1"},
    }


def v2_tool_payload() -> dict[str, object]:
    card = tool_payload()["tarot"]
    assert isinstance(card, dict)
    return {
        "record_id": "starpath-v2-capture-test",
        "generated_at": "2026-08-22T00:00:00Z",
        "mode": "daily",
        "star": tool_payload()["star"],
        "tarot": {
            "spread": "three_card",
            "cards": [
                {**card, "id": "major-00", "position": "past", "order": 0},
                {**card, "id": "major-01", "position": "present", "order": 1},
                {**card, "id": "major-02", "position": "future", "order": 2},
            ],
        },
        "quote": tool_payload()["quote"],
        "metadata": {"contract_version": "starpath.tool.v2"},
    }


def tool_result(payload: object | None = None) -> CallToolResult:
    raw = json.dumps(tool_payload() if payload is None else payload, ensure_ascii=False)
    return CallToolResult([TextContent("text", raw)])


def test_extractor_returns_only_astrbot_text_content() -> None:
    raw = ToolResultExtractor().extract(tool_result())

    assert json.loads(raw)["record_id"] == "starpath-capture-test"
    with pytest.raises(ToolResultExtractionError):
        ToolResultExtractor().extract(None)
    with pytest.raises(ToolResultExtractionError):
        ToolResultExtractor().extract(CallToolResult([]))
    with pytest.raises(ToolResultExtractionError):
        ToolResultExtractor().extract(CallToolResult([object()]))
    with pytest.raises(ToolResultExtractionError):
        ToolResultExtractor().extract(CallToolResult([TextContent("text", " ")]))


def test_parser_reconstructs_every_required_domain_object() -> None:
    record = StarpathToolResultParser().parse(ToolResultExtractor().extract(tool_result()))

    assert record.record_id == "starpath-capture-test"
    assert record.star.zh_name == "织女星"
    assert record.star.astronomy == "A real nearby star."
    assert record.tarot.card.id == "major-00"
    assert record.tarot.card.upright_meaning == ("openness",)
    assert record.tarot.orientation == "upright"
    assert record.tarot.keywords == ("beginnings",)
    assert record.tarot.meaning == ("openness",)
    assert record.quote.theme == "exploration"


@pytest.mark.parametrize("raw", [None, "not json", "[]", "{}"])
def test_parser_rejects_non_contract_json(raw: object) -> None:
    with pytest.raises(InvalidStarpathToolResultError):
        StarpathToolResultParser().parse(raw)  # type: ignore[arg-type]


def test_parser_rejects_missing_or_empty_tarot_identity() -> None:
    missing = tool_payload()
    missing["tarot"] = {}
    with pytest.raises(MissingTarotCardError):
        StarpathToolResultParser().parse(json.dumps(missing))

    empty = tool_payload()
    empty["tarot"] = {**empty["tarot"], "id": ""}
    with pytest.raises(MissingTarotCardError):
        StarpathToolResultParser().parse(json.dumps(empty))


def test_capture_composes_extraction_parsing_and_event_extra_without_delivery() -> None:
    event = Event()
    application = Application()
    hook = StarpathExperienceCaptureHook.from_tool_result(
        ToolResultExtractor(),
        StarpathToolResultParser(),
        application,  # type: ignore[arg-type]
        PresentationBuilder(),  # type: ignore[arg-type]
        ConfigDeckProvider({"default_deck_id": "configured_deck"}),
    )

    asyncio.run(hook.capture(event, Tool(), {"spread": "single"}, tool_result()))

    record, deck_id, spread = application.calls[0]
    assert record.record_id == "starpath-capture-test"
    assert (deck_id, spread) == ("configured_deck", "single")
    assert isinstance(event.extras[PRESENTATION_EXTRA_KEY], PresentationResult)
    assert event.extras[CAPTURE_STATUS_EXTRA_KEY] == "captured"


def test_capture_dispatches_v2_to_the_multi_card_application_input() -> None:
    event = Event()
    application = Application()
    hook = StarpathExperienceCaptureHook.from_tool_result(
        ToolResultExtractor(),
        StarpathToolResultParser(),
        application,  # type: ignore[arg-type]
        PresentationBuilder(),  # type: ignore[arg-type]
        ConfigDeckProvider({"default_deck_id": "configured_deck"}),
    )

    asyncio.run(hook.capture(event, Tool(), {"spread": "single"}, tool_result(v2_tool_payload())))

    assert application.calls == []
    assert len(application.input_calls) == 1
    experience_input = application.input_calls[0]
    assert experience_input.spread == "three_card"
    assert [card.position.value for card in experience_input.cards] == [
        "past",
        "present",
        "future",
    ]
    assert event.extras[CAPTURE_STATUS_EXTRA_KEY] == "captured"


def test_capture_failure_is_stored_and_never_raises_or_sends() -> None:
    event = Event()
    hook = StarpathExperienceCaptureHook.from_tool_result(
        ToolResultExtractor(),
        StarpathToolResultParser(),
        Application(),  # type: ignore[arg-type]
        PresentationBuilder(),  # type: ignore[arg-type]
        ConfigDeckProvider(None),
    )

    asyncio.run(hook.capture(event, Tool(), {}, tool_result()))

    assert event.extras == {CAPTURE_STATUS_EXTRA_KEY: "failed"}


def test_deck_provider_is_injected_and_never_uses_tool_result_data() -> None:
    assert ConfigDeckProvider({"default_deck_id": "deck_from_runtime"}).get_default_deck_id() == (
        "deck_from_runtime"
    )
    with pytest.raises(MissingDefaultDeckError):
        ConfigDeckProvider({}).get_default_deck_id()


def test_package_deck_provider_uses_the_single_packaged_deck_without_new_config() -> None:
    manifest_root = Path(__file__).resolve().parents[1] / "assets" / "tarot"

    assert PackageDeckProvider(manifest_root, None).get_default_deck_id() == (
        "dark_cosmic_archive"
    )


def test_capture_modules_have_no_message_or_image_delivery_calls() -> None:
    root = Path(__file__).resolve().parents[1]
    content = "\n".join(
        (root / "experience" / name).read_text(encoding="utf-8")
        for name in (
            "tool_result_parser.py",
            "tool_contract_dispatcher.py",
            "post_tool_capture.py",
            "deck_provider.py",
        )
    ).lower()

    for forbidden in ("event.send(", "messagechain", "image(", "on_decorating_result"):
        assert forbidden not in content
