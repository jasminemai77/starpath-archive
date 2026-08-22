"""Platform-isolated contracts for adapting generic display resources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .asset_consumer import DisplayResource


class AdapterConversionError(ValueError):
    """Base error for a failed platform-payload conversion."""


class InvalidDisplayResourceError(AdapterConversionError):
    """Raised when a display resource lacks valid conversion metadata."""


class UnsupportedResourceTypeError(AdapterConversionError):
    """Raised when a generic adapter cannot represent a resource type."""


@dataclass(frozen=True)
class PlatformPayload:
    """Platform-neutral payload metadata for a future platform-specific sender."""

    payload_type: str
    content: str
    metadata: dict[str, str]

    @classmethod
    def from_display_resource(cls, resource: DisplayResource | None) -> "PlatformPayload":
        """Adapt display metadata without performing any transport or file I/O."""
        if resource is None:
            raise InvalidDisplayResourceError("A display resource is required for adaptation")
        if resource.resource_type != "image":
            raise UnsupportedResourceTypeError(
                f"Unsupported display resource type: {resource.resource_type}"
            )
        if not isinstance(resource.path, str) or not resource.path:
            raise InvalidDisplayResourceError("A display resource path is required")
        if not isinstance(resource.format, str) or resource.format.lower() != "png":
            raise InvalidDisplayResourceError("A PNG display resource format is required")

        return cls(
            payload_type="image",
            content=resource.path,
            metadata={"format": resource.format, **resource.metadata},
        )


class PlatformAdapter(ABC):
    """Convert generic display metadata into a generic platform payload."""

    @abstractmethod
    def adapt(self, resource: DisplayResource) -> PlatformPayload:
        """Return a payload description or raise an explicit adapter error."""
        raise NotImplementedError
