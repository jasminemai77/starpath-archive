"""Tests for the platform-neutral complete-message presentation model."""

from __future__ import annotations

import ast
import inspect

import pytest
from starpath_plugin.experience import message_presentation
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.message_presentation import (
    MessagePresentation,
    MessagePresentationError,
    MessageSection,
    PresentationResultMessageConverter,
)
from starpath_plugin.experience.presentation import (
    ImagePresentation,
    PresentationResult,
    TextPresentation,
)


def resource(path: str = "major/00_the_fool.png") -> DisplayResource:
    return DisplayResource(
        resource_type="image",
        path=path,
        format="png",
        metadata={"deck_id": "dark_cosmic_archive", "card_id": "major-00"},
    )


def test_single_card_message_model_keeps_title_sections_and_footer() -> None:
    message = MessagePresentation(
        title="Starpath Archive",
        subtitle="Daily record",
        sections=(MessageSection("Tarot", "The Fool", 0),),
        resources=(resource(),),
        footer="Symbolic entertainment.",
    )

    assert message.title == "Starpath Archive"
    assert message.subtitle == "Daily record"
    assert message.sections[0].content == "The Fool"
    assert message.footer == "Symbolic entertainment."


def test_message_resources_retain_existing_display_resource_references() -> None:
    card_resource = resource()
    message = MessagePresentation(
        title="Cards",
        subtitle=None,
        sections=(),
        resources=(card_resource,),
        footer=None,
    )

    assert message.resources[0] is card_resource


def test_sections_are_sorted_by_explicit_order_for_multi_card_future_layouts() -> None:
    message = MessagePresentation(
        title="Three cards",
        subtitle=None,
        sections=(
            MessageSection("Outcome", "Third", 2),
            MessageSection("Present", "Second", 1),
            MessageSection("Past", "First", 0),
        ),
        resources=(resource("major/00_the_fool.png"), resource("major/01_the_magician.png")),
        footer=None,
    )

    assert [section.title for section in message.sections] == ["Past", "Present", "Outcome"]


def test_empty_resources_are_a_supported_text_only_degradation() -> None:
    message = MessagePresentation(
        title="Text only",
        subtitle=None,
        sections=(MessageSection("Quote", "A symbolic reference.", 0),),
        resources=(),
        footer=None,
    )

    assert message.resources == ()


def test_legacy_presentation_result_converts_without_changing_existing_contracts() -> None:
    card_resource = resource()
    legacy = PresentationResult(
        title="Tarot experience",
        mode="quick",
        sections=(
            TextPresentation("title", "Title", "Tarot experience"),
            ImagePresentation(card_resource),
            TextPresentation("tarot", "Tarot", "main: major-00"),
            TextPresentation("fortune", "Quote", "A symbolic reference."),
        ),
    )

    message = PresentationResultMessageConverter().convert(legacy)

    assert message.title == legacy.title
    assert [section.title for section in message.sections] == ["Tarot", "Quote"]
    assert message.resources == (card_resource,)
    assert message.subtitle is None
    assert message.footer is None


@pytest.mark.parametrize(
    "value",
    [
        MessageSection("Duplicate", "one", 0),
        MessageSection("Duplicate", "two", 0),
    ],
)
def test_duplicate_section_orders_are_rejected(value: MessageSection) -> None:
    with pytest.raises(MessagePresentationError):
        MessagePresentation("x", None, (value, MessageSection("Other", "x", 0)), (), None)


def test_message_model_has_no_platform_or_runtime_dependencies() -> None:
    tree = ast.parse(inspect.getsource(message_presentation))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "event",
            "send",
            "messagechain",
            "astrbot",
            "onebot",
            "napcat",
            "qq",
            "runtime",
            "llm",
        }
    )
