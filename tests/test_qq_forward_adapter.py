"""Tests for the no-transport QQ Forward payload adapter."""

from __future__ import annotations

import ast
import inspect

from starpath_plugin.adapter import qq_forward
from starpath_plugin.adapter.qq_forward import QQForwardMessageAdapter
from starpath_plugin.experience.asset_consumer import DisplayResource
from starpath_plugin.experience.message_presentation import (
    MessagePresentation,
    MessageSection,
)


def resource(path: str = "major/00_the_fool.png") -> DisplayResource:
    return DisplayResource(
        resource_type="image",
        path=path,
        format="png",
        metadata={"deck_id": "dark_cosmic_archive", "card_id": "major-00"},
    )


def message(*, resources: tuple[DisplayResource, ...] = (resource(),)) -> MessagePresentation:
    return MessagePresentation(
        title="Starpath Archive",
        subtitle="Daily record",
        sections=(
            MessageSection("Tarot", "The Fool", 0),
            MessageSection("Quote", "A symbolic reference.", 1),
        ),
        resources=resources,
        footer="Symbolic entertainment.",
    )


def test_single_card_message_converts_to_header_sections_resource_and_footer_nodes() -> None:
    presentation = message()
    payload = QQForwardMessageAdapter().adapt(presentation)

    assert payload.title == "Starpath Archive"
    assert [node.node_type for node in payload.nodes] == [
        "text",
        "text",
        "text",
        "resource",
        "text",
    ]
    assert payload.nodes[0].text == "Starpath Archive\nDaily record"
    assert payload.nodes[1].text == "Tarot\nThe Fool"
    assert payload.nodes[3].resource is presentation.resources[0]
    assert payload.nodes[-1].text == "Symbolic entertainment."


def test_multiple_sections_keep_the_message_model_order() -> None:
    presentation = MessagePresentation(
        title="Spread",
        subtitle=None,
        sections=(
            MessageSection("Outcome", "Third", 2),
            MessageSection("Past", "First", 0),
            MessageSection("Present", "Second", 1),
        ),
        resources=(),
        footer=None,
    )

    payload = QQForwardMessageAdapter().adapt(presentation)

    assert [node.text for node in payload.nodes] == [
        "Spread",
        "Past\nFirst",
        "Present\nSecond",
        "Outcome\nThird",
    ]


def test_multiple_image_resources_become_ordered_resource_nodes() -> None:
    first, second = resource(), resource("major/01_the_magician.png")

    payload = QQForwardMessageAdapter().adapt(message(resources=(first, second)))

    resource_nodes = [node for node in payload.nodes if node.node_type == "resource"]
    assert [node.resource for node in resource_nodes] == [first, second]


def test_no_image_degrades_to_text_nodes_without_changing_section_content() -> None:
    payload = QQForwardMessageAdapter().adapt(message(resources=()))

    assert all(node.node_type == "text" for node in payload.nodes)
    assert [node.text for node in payload.nodes] == [
        "Starpath Archive\nDaily record",
        "Tarot\nThe Fool",
        "Quote\nA symbolic reference.",
        "Symbolic entertainment.",
    ]


def test_adapter_has_no_onebot_send_connection_or_runtime_dependencies() -> None:
    tree = ast.parse(inspect.getsource(qq_forward))
    identifiers = {
        node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert identifiers.isdisjoint(
        {
            "send",
            "event",
            "astrbot",
            "onebot",
            "napcat",
            "runtime",
            "connection",
            "call_action",
        }
    )
