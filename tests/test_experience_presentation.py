"""Tests for the platform-neutral ExperienceResult presentation boundary."""

from __future__ import annotations

import ast
import inspect
import json
from datetime import datetime, timezone

import pytest
from starpath_plugin.adapter import StarpathToolAdapter
from starpath_plugin.core import QuoteEngine, StarEngine, StarpathService, TarotEngine
from starpath_plugin.core.repository import load_quotes, load_stars, load_tarot_cards
from starpath_plugin.experience import presentation
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.presentation import (
    ExperiencePresentationBuilder,
    ImagePresentation,
    PresentationInputError,
    TextPresentation,
)
from starpath_plugin.experience.tarot import (
    ExperienceResult,
    ExperienceTextSection,
    TarotCardSelection,
)


def build_experience(*, with_image: bool = True) -> ExperienceResult:
    resources = ()
    if with_image:
        resources = (
            DisplayResource(
                resource_type="image",
                path="major/00_the_fool.png",
                format="png",
                metadata={"deck_id": "a_visual_deck", "card_id": "major-00"},
            ),
        )
    return ExperienceResult(
        title="Tarot experience",
        spread="single",
        cards=(TarotCardSelection(card_id="major-00", position="main"),),
        display_resources=resources,
        text_sections=(
            ExperienceTextSection("tarot", "Tarot", "main: major-00"),
            ExperienceTextSection("fortune_sign", "Fortune sign", "Symbolic reference."),
        ),
        fortune_context=None,
    )


def test_quick_presentation_orders_title_image_and_text_without_changing_resource() -> None:
    experience = build_experience()
    result = ExperiencePresentationBuilder().build(experience, mode="quick")

    assert result.title == experience.title
    assert result.mode == "quick"
    assert isinstance(result.sections[0], TextPresentation)
    assert isinstance(result.sections[1], ImagePresentation)
    assert result.sections[1].resource is experience.display_resources[0]
    text_ids = [
        section.section_id
        for section in result.sections
        if isinstance(section, TextPresentation)
    ]
    assert text_ids == [
        "title",
        "tarot",
        "fortune_sign",
    ]


def test_presentation_degrades_to_text_when_no_display_resources_exist() -> None:
    result = ExperiencePresentationBuilder().build(build_experience(with_image=False), mode="quick")

    assert all(not isinstance(section, ImagePresentation) for section in result.sections)
    text_ids = [
        section.section_id
        for section in result.sections
        if isinstance(section, TextPresentation)
    ]
    assert text_ids == [
        "title",
        "tarot",
        "fortune_sign",
    ]


def test_full_mode_is_parameter_supported_without_implementing_a_spread_layout() -> None:
    result = ExperiencePresentationBuilder().build(build_experience(), mode="full")

    assert result.mode == "full"
    with pytest.raises(PresentationInputError):
        ExperiencePresentationBuilder().build(build_experience(), mode="unknown")


def test_presentation_has_no_platform_message_or_resolver_dependencies() -> None:
    tree = ast.parse(inspect.getsource(presentation))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "resolve",
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
async def test_presentation_does_not_change_existing_tool_contract() -> None:
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
