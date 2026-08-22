"""Structured experience composition for Native Agent tool results."""

from .application import TarotExperienceApplication
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
    "ExperienceResult",
    "ExperienceTextSection",
    "FortuneContext",
    "InvalidStarpathRecordError",
    "MissingDeckContextError",
    "MissingTarotCardError",
    "StarpathExperience",
    "StarpathRecordExperienceAdapter",
    "TarotCardSelection",
    "TarotExperienceApplication",
    "TarotExperienceInput",
    "TarotExperienceOrchestrator",
]
