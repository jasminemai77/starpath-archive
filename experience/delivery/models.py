"""Immutable metadata returned by the runtime image preparation boundary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PreparedAstrBotResource:
    """A validated local image location ready for a future runtime sender."""

    resource_type: str
    resolved_path: str
    media_type: str
    metadata: dict[str, str]
