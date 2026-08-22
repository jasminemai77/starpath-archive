"""Platform-neutral message model for a complete Starpath experience."""

from __future__ import annotations

from dataclasses import dataclass

from .asset_consumer import DisplayResource
from .presentation import PresentationResult, TextPresentation


class MessagePresentationError(ValueError):
    """Raised when a message presentation cannot safely describe its content."""


@dataclass(frozen=True)
class MessageSection:
    """One ordered text section in a complete display message."""

    title: str
    content: str
    order: int

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise MessagePresentationError("A message section requires a title")
        if not isinstance(self.content, str) or not self.content.strip():
            raise MessagePresentationError("A message section requires content")
        if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order < 0:
            raise MessagePresentationError("A message section requires a non-negative order")


@dataclass(frozen=True)
class MessagePresentation:
    """One complete, platform-neutral Starpath experience message.

    ``resources`` retains existing ``DisplayResource`` values rather than
    introducing a second image model.  It can represent no resource, one card,
    or multiple future card resources without deciding how a platform delivers
    them.
    """

    title: str
    subtitle: str | None
    sections: tuple[MessageSection, ...]
    resources: tuple[DisplayResource, ...]
    footer: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise MessagePresentationError("A message presentation requires a title")
        if self.subtitle is not None and (
            not isinstance(self.subtitle, str) or not self.subtitle.strip()
        ):
            raise MessagePresentationError("A subtitle must be non-empty when provided")
        if self.footer is not None and (
            not isinstance(self.footer, str) or not self.footer.strip()
        ):
            raise MessagePresentationError("A footer must be non-empty when provided")
        if not all(isinstance(section, MessageSection) for section in self.sections):
            raise MessagePresentationError("Sections must be MessageSection values")
        if len({section.order for section in self.sections}) != len(self.sections):
            raise MessagePresentationError("Message section orders must be unique")
        if not all(isinstance(resource, DisplayResource) for resource in self.resources):
            raise MessagePresentationError("Resources must be DisplayResource values")

        ordered_sections = tuple(sorted(self.sections, key=lambda section: section.order))
        object.__setattr__(self, "sections", ordered_sections)


class PresentationResultMessageConverter:
    """Convert the legacy presentation plan without modifying existing consumers."""

    def convert(self, presentation: PresentationResult) -> MessagePresentation:
        """Return a message model retaining legacy text ordering and resource identity."""
        if not isinstance(presentation, PresentationResult):
            raise MessagePresentationError("Expected a PresentationResult")

        sections: list[MessageSection] = []
        resources: list[DisplayResource] = []
        for index, section in enumerate(presentation.sections):
            if isinstance(section, TextPresentation):
                if section.section_id != "title":
                    sections.append(MessageSection(section.title, section.content, index))
            else:
                resource = getattr(section, "resource", None)
                if isinstance(resource, DisplayResource):
                    resources.append(resource)
                else:
                    raise MessagePresentationError("Legacy presentation has an invalid section")

        return MessagePresentation(
            title=presentation.title,
            subtitle=None,
            sections=tuple(sections),
            resources=tuple(resources),
            footer=None,
        )
