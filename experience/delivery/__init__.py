"""Runtime resource preparation contracts without platform delivery side effects."""

from .errors import (
    InvalidRuntimeResourceError,
    RuntimePayloadPreparationError,
    RuntimeResourceAccessError,
    RuntimeResourceNotFoundError,
)
from .interface import RuntimeImageDelivery
from .local import LocalRuntimeImageDelivery
from .models import PreparedAstrBotResource

__all__ = [
    "InvalidRuntimeResourceError",
    "LocalRuntimeImageDelivery",
    "PreparedAstrBotResource",
    "RuntimeImageDelivery",
    "RuntimePayloadPreparationError",
    "RuntimeResourceAccessError",
    "RuntimeResourceNotFoundError",
]
