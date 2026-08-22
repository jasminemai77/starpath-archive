"""Platform-neutral contract for consuming ordered presentation plans."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .asset_consumer import DisplayResource
from .presentation import (
    ImagePresentation,
    PresentationResult,
    PresentationSection,
    TextPresentation,
)


class PresentationConversionError(ValueError):
    """Base error for a failed platform-neutral presentation conversion."""


class InvalidPresentationResultError(PresentationConversionError):
    """Raised when a consumer receives something other than a presentation result."""


class UnsupportedPresentationSectionError(PresentationConversionError):
    """Raised when a consumer cannot represent an ordered presentation section."""


@dataclass(frozen=True)
class TextElement:
    """A platform-neutral text element."""

    section_id: str
    title: str
    content: str


@dataclass(frozen=True)
class ResourceElement:
    """A platform-neutral resource element retaining the original reference."""

    resource: DisplayResource


PlatformElement = TextElement | ResourceElement


@dataclass(frozen=True)
class PlatformPresentation:
    """Ordered platform-neutral elements awaiting a future platform implementation."""

    title: str
    mode: str
    elements: tuple[PlatformElement, ...]


class PresentationConsumer(ABC):
    """Convert a PresentationResult; runtime delivery is intentionally out of scope."""

    @abstractmethod
    def consume(self, presentation: PresentationResult) -> PlatformPresentation:
        """Return a platform-neutral element sequence."""
        raise NotImplementedError


class StructuredPresentationConsumer(PresentationConsumer):
    """Reference converter for the common text and resource presentation sections."""

    def consume(self, presentation: PresentationResult) -> PlatformPresentation:
        """Convert sections without inspecting or transforming resource content."""
        if not isinstance(presentation, PresentationResult):
            raise InvalidPresentationResultError("Expected a PresentationResult")
        return PlatformPresentation(
            title=presentation.title,
            mode=presentation.mode,
            elements=tuple(self._convert(section) for section in presentation.sections),
        )

    @staticmethod
    def _convert(section: PresentationSection) -> PlatformElement:
        if isinstance(section, TextPresentation):
            return TextElement(section.section_id, section.title, section.content)
        if isinstance(section, ImagePresentation):
            return ResourceElement(section.resource)
        raise UnsupportedPresentationSectionError(
            f"Unsupported presentation section: {type(section).__name__}"
        )
