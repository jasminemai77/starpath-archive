"""Platform-neutral presentation structures derived from an experience result."""

from __future__ import annotations

from dataclasses import dataclass

from .asset_consumer import DisplayResource
from .tarot import ExperienceResult, ExperienceTextSection


class PresentationInputError(ValueError):
    """Raised when a requested presentation mode is not supported."""


@dataclass(frozen=True)
class TextPresentation:
    """One ordered text block, preserving its source-backed section metadata."""

    section_id: str
    title: str
    content: str

    @classmethod
    def from_experience_section(cls, section: ExperienceTextSection) -> "TextPresentation":
        return cls(section_id=section.section_id, title=section.title, content=section.content)


@dataclass(frozen=True)
class ImagePresentation:
    """One ordered, untouched display resource reference."""

    resource: DisplayResource


PresentationSection = TextPresentation | ImagePresentation


@dataclass(frozen=True)
class PresentationResult:
    """A platform-neutral ordered display plan with no message components."""

    title: str
    mode: str
    sections: tuple[PresentationSection, ...]


class ExperiencePresentationBuilder:
    """Arrange existing experience data; never resolve, read, or deliver media."""

    _SUPPORTED_MODES = frozenset({"quick", "full"})

    def build(self, experience_result: ExperienceResult, *, mode: str) -> PresentationResult:
        """Build a title-first ordered presentation and omit unavailable images safely."""
        if mode not in self._SUPPORTED_MODES:
            raise PresentationInputError(f"Unsupported presentation mode: {mode}")

        title = TextPresentation(
            section_id="title", title="Title", content=experience_result.title
        )
        images = tuple(
            ImagePresentation(resource=resource)
            for resource in experience_result.display_resources
        )
        text_sections = tuple(
            TextPresentation.from_experience_section(section)
            for section in experience_result.text_sections
        )
        return PresentationResult(
            title=experience_result.title,
            mode=mode,
            sections=(title, *images, *text_sections),
        )
