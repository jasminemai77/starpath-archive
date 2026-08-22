"""Structured experience composition for Native Agent tool results."""

from .application import TarotExperienceApplication
from .presentation import (
    ExperiencePresentationBuilder,
    ImagePresentation,
    PresentationInputError,
    PresentationResult,
    TextPresentation,
)
from .record import StarpathExperience
from .record_adapter import (
    InvalidStarpathRecordError,
    MissingDeckContextError,
    MissingTarotCardError,
    StarpathRecordExperienceAdapter,
)
from .tarot import (
    ExperienceBuildError,
    ExperienceInputError,
    ExperienceResult,
    ExperienceTextSection,
    FortuneContext,
    TarotCardSelection,
    TarotExperienceInput,
    TarotExperienceOrchestrator,
)

__all__ = [
    "ExperienceBuildError",
    "ExperienceInputError",
    "ExperiencePresentationBuilder",
    "ExperienceResult",
    "ExperienceTextSection",
    "FortuneContext",
    "InvalidStarpathRecordError",
    "ImagePresentation",
    "MissingDeckContextError",
    "MissingTarotCardError",
    "PresentationInputError",
    "PresentationResult",
    "StarpathExperience",
    "StarpathRecordExperienceAdapter",
    "TarotCardSelection",
    "TarotExperienceApplication",
    "TarotExperienceInput",
    "TarotExperienceOrchestrator",
    "TextPresentation",
]
