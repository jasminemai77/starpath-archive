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
        text_sections = tuple(
            TextPresentation.from_experience_section(section)
            for section in experience_result.text_sections
        )
        if experience_result.spread == "three_card":
            sections = self._three_card_sections(experience_result, title, text_sections)
        else:
            images = tuple(
                ImagePresentation(resource=resource)
                for resource in experience_result.display_resources
            )
            sections = (title, *images, *text_sections)
        return PresentationResult(
            title=experience_result.title,
            mode=mode,
            sections=sections,
        )

    @staticmethod
    def _three_card_sections(
        experience_result: ExperienceResult,
        title: TextPresentation,
        text_sections: tuple[TextPresentation, ...],
    ) -> tuple[PresentationSection, ...]:
        """Keep a card's resource adjacent to its ordered position section."""
        resources_by_card_id = {
            resource.metadata.get("card_id"): resource
            for resource in experience_result.display_resources
        }
        text_by_id = {section.section_id: section for section in text_sections}
        sections: list[PresentationSection] = [title]
        consumed_text_ids: set[str] = set()

        for selection in experience_result.cards:
            resource = resources_by_card_id.get(selection.card_id)
            if resource is not None:
                sections.append(ImagePresentation(resource=resource))
            section_id = f"tarot_{selection.position.value}"
            text_section = text_by_id.get(section_id)
            if text_section is not None:
                sections.append(text_section)
                consumed_text_ids.add(section_id)

        sections.extend(
            section for section in text_sections if section.section_id not in consumed_text_ids
        )
        return tuple(sections)
