"""Tests for the dependency-injected Tarot experience application service."""

from __future__ import annotations

import ast
import inspect
import json
from datetime import datetime, timezone

import pytest
from starpath_plugin.adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards
from starpath_plugin.core.resolver import AssetNotFoundError
from starpath_plugin.experience import application
from starpath_plugin.experience.application import TarotExperienceApplication
from starpath_plugin.experience.tarot import (
    ExperienceInputError,
    ExperienceResult,
    TarotCardSelection,
    TarotExperienceInput,
)


class RecordingAdapter:
    def __init__(self, experience_input: TarotExperienceInput) -> None:
        self.experience_input = experience_input
        self.calls: list[tuple[object, str, str]] = []

    def adapt(self, record: object, *, deck_id: str, spread: str) -> TarotExperienceInput:
        self.calls.append((record, deck_id, spread))
        return self.experience_input


class RecordingOrchestrator:
    def __init__(self, result: ExperienceResult) -> None:
        self.result = result
        self.calls: list[TarotExperienceInput] = []

    def build(self, experience_input: TarotExperienceInput) -> ExperienceResult:
        self.calls.append(experience_input)
        return self.result


def build_input() -> TarotExperienceInput:
    return TarotExperienceInput(
        deck_id="caller_selected_deck",
        spread="single",
        cards=(TarotCardSelection(card_id="major-00", position="main"),),
    )


def build_result() -> ExperienceResult:
    return ExperienceResult(
        title="Tarot experience",
        spread="single",
        cards=(TarotCardSelection(card_id="major-00", position="main"),),
        display_resources=(),
        text_sections=(),
        fortune_context=None,
    )


def test_application_delegates_record_deck_and_spread_without_changing_result() -> None:
    experience_input = build_input()
    expected_result = build_result()
    adapter = RecordingAdapter(experience_input)
    orchestrator = RecordingOrchestrator(expected_result)
    record = object()

    result = TarotExperienceApplication(adapter, orchestrator).build(  # type: ignore[arg-type]
        record,
        deck_id="caller_selected_deck",
        spread="single",
    )

    assert result is expected_result
    assert adapter.calls == [(record, "caller_selected_deck", "single")]
    assert orchestrator.calls == [experience_input]


def test_application_propagates_existing_adapter_and_orchestrator_errors() -> None:
    experience_input = build_input()

    class FailingAdapter(RecordingAdapter):
        def adapt(self, record: object, *, deck_id: str, spread: str) -> TarotExperienceInput:
            raise ExperienceInputError("invalid experience input")

    class FailingOrchestrator(RecordingOrchestrator):
        def build(self, experience_input: TarotExperienceInput) -> ExperienceResult:
            raise AssetNotFoundError("caller_selected_deck", "major-00")

    with pytest.raises(ExperienceInputError):
        failing_adapter_application = TarotExperienceApplication(
            FailingAdapter(experience_input),  # type: ignore[arg-type]
            RecordingOrchestrator(build_result()),  # type: ignore[arg-type]
        )
        failing_adapter_application.build(
            object(), deck_id="caller_selected_deck", spread="single"
        )
    with pytest.raises(AssetNotFoundError):
        failing_orchestrator_application = TarotExperienceApplication(
            RecordingAdapter(experience_input),  # type: ignore[arg-type]
            FailingOrchestrator(build_result()),  # type: ignore[arg-type]
        )
        failing_orchestrator_application.build(
            object(), deck_id="caller_selected_deck", spread="single"
        )


def test_application_has_no_platform_agent_or_message_dependencies() -> None:
    tree = ast.parse(inspect.getsource(application))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "event",
            "send",
            "send_message",
            "chain_result",
            "messagechain",
            "astrbot",
            "onebot",
            "napcat",
            "llm",
            "user_data",
        }
    )


class Event:
    def get_sender_id(self) -> str:
        return "tool-contract-test"


@pytest.mark.asyncio
async def test_application_does_not_change_the_existing_tool_contract() -> None:
    service = StarpathService(
        StarEngine(load_stars()), TarotEngine(load_tarot_cards()), QuoteEngine(load_quotes())
    )
    tool = StarpathToolAdapter(
        service,
        now=lambda: datetime(2026, 8, 22, 9, 30, tzinfo=timezone.utc),
    )

    payload = json.loads(await tool.generate(Event()))

    assert payload["metadata"]["contract_version"] == "starpath.tool.v1"
    assert {"image_path", "image_url", "asset_key", "display_resources"}.isdisjoint(
        payload
    )
