"""QQ Forward payload design derived from platform-neutral message presentation."""

from __future__ import annotations

from dataclasses import dataclass

from ..experience.asset_consumer import DisplayResource
from ..experience.message_presentation import MessagePresentation


class QQForwardPayloadError(ValueError):
    """Raised when a forward payload cannot faithfully represent a message model."""


@dataclass(frozen=True)
class QQForwardNode:
    """One semantic forward node containing text or an existing resource reference.

    Sender identity, session identity, component construction, serialization,
    connection, and dispatch intentionally remain outside this payload model.
    """

    node_type: str
    text: str | None = None
    resource: DisplayResource | None = None

    def __post_init__(self) -> None:
        if self.node_type == "text":
            if not isinstance(self.text, str) or not self.text.strip() or self.resource is not None:
                raise QQForwardPayloadError("A text forward node requires text only")
        elif self.node_type == "resource":
            if not isinstance(self.resource, DisplayResource) or self.text is not None:
                raise QQForwardPayloadError("A resource forward node requires a resource only")
        else:
            raise QQForwardPayloadError(f"Unsupported forward node type: {self.node_type}")


@dataclass(frozen=True)
class QQForwardPayload:
    """Ordered QQ-forward-ready semantic nodes with no transport behaviour."""

    title: str
    nodes: tuple[QQForwardNode, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise QQForwardPayloadError("A forward payload requires a title")
        if not self.nodes or not all(isinstance(node, QQForwardNode) for node in self.nodes):
            raise QQForwardPayloadError("A forward payload requires ordered nodes")


class QQForwardMessageAdapter:
    """Convert a complete message presentation into semantic QQ forward nodes only."""

    def adapt(self, presentation: MessagePresentation) -> QQForwardPayload:
        """Arrange header, ordered sections, resources, and footer deterministically."""
        if not isinstance(presentation, MessagePresentation):
            raise QQForwardPayloadError("Expected a MessagePresentation")

        nodes = [QQForwardNode("text", text=self._header(presentation))]
        nodes.extend(
            QQForwardNode("text", text=f"{section.title}\n{section.content}")
            for section in presentation.sections
        )
        nodes.extend(
            QQForwardNode("resource", resource=resource)
            for resource in presentation.resources
        )
        if presentation.footer is not None:
            nodes.append(QQForwardNode("text", text=presentation.footer))
        return QQForwardPayload(title=presentation.title, nodes=tuple(nodes))

    @staticmethod
    def _header(presentation: MessagePresentation) -> str:
        if presentation.subtitle is None:
            return presentation.title
        return f"{presentation.title}\n{presentation.subtitle}"
