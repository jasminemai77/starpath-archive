"""Structured experience composition for Native Agent tool results."""

from .application import TarotExperienceApplication
from .message_presentation import (
    MessagePresentation,
    MessagePresentationError,
    MessageSection,
    PresentationResultMessageConverter,
)
from .presentation import (
    ExperiencePresentationBuilder,
    ImagePresentation,
    PresentationInputError,
    PresentationResult,
    TextPresentation,
)
from .presentation_consumer import (
    InvalidPresentationResultError,
    PlatformPresentation,
    PresentationConsumer,
    PresentationConversionError,
    ResourceElement,
    StructuredPresentationConsumer,
    TextElement,
    UnsupportedPresentationSectionError,
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
    "InvalidPresentationResultError",
    "ImagePresentation",
    "MissingDeckContextError",
    "MissingTarotCardError",
    "MessagePresentation",
    "MessagePresentationError",
    "MessageSection",
    "PresentationInputError",
    "PlatformPresentation",
    "PresentationConsumer",
    "PresentationConversionError",
    "PresentationResult",
    "PresentationResultMessageConverter",
    "StarpathExperience",
    "StarpathRecordExperienceAdapter",
    "StructuredPresentationConsumer",
    "TarotCardSelection",
    "TarotExperienceApplication",
    "TarotExperienceInput",
    "TarotExperienceOrchestrator",
    "TextPresentation",
    "TextElement",
    "ResourceElement",
    "UnsupportedPresentationSectionError",
]
