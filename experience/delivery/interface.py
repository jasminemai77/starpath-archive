"""Abstract prepare-only runtime image delivery boundary."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...adapter.astrbot_platform import AstrBotImagePayload
from .models import PreparedAstrBotResource


class RuntimeImageDelivery(ABC):
    """Prepare an AstrBot image resource without constructing or sending a message."""

    @abstractmethod
    def prepare(self, payload: AstrBotImagePayload) -> PreparedAstrBotResource:
        """Return a safe prepared resource or raise a runtime delivery error."""
        raise NotImplementedError
