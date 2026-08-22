"""Contract tests for platform-neutral presentation consumption."""

from __future__ import annotations

import ast
import inspect

import pytest
from starpath_plugin.experience import presentation_consumer
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.presentation import (
    ImagePresentation,
    PresentationResult,
    TextPresentation,
)
from starpath_plugin.experience.presentation_consumer import (
    ResourceElement,
    StructuredPresentationConsumer,
    TextElement,
    UnsupportedPresentationSectionError,
)


def build_presentation() -> PresentationResult:
    resource = DisplayResource("image", "major/00_the_fool.png", "png", {"card_id": "major-00"})
    return PresentationResult(
        title="Tarot experience",
        mode="quick",
        sections=(
            TextPresentation("title", "Title", "Tarot experience"),
            ImagePresentation(resource),
        ),
    )


def test_consumer_converts_text_and_image_while_preserving_resource_reference() -> None:
    presentation = build_presentation()
    result = StructuredPresentationConsumer().consume(presentation)

    assert isinstance(result.elements[0], TextElement)
    assert isinstance(result.elements[1], ResourceElement)
    assert result.elements[1].resource is presentation.sections[1].resource


def test_consumer_rejects_an_unknown_section() -> None:
    presentation = PresentationResult("x", "quick", sections=(object(),))  # type: ignore[arg-type]

    with pytest.raises(UnsupportedPresentationSectionError):
        StructuredPresentationConsumer().consume(presentation)


def test_consumer_has_no_platform_send_or_file_dependencies() -> None:
    tree = ast.parse(inspect.getsource(presentation_consumer))
    names = {node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)} | {
        node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert names.isdisjoint(
        {"open", "send", "event", "astrbot", "onebot", "napcat", "llm", "user_data"}
    )
