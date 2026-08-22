"""AstrBot-specific payload design without runtime or transport integration."""

from __future__ import annotations

from dataclasses import dataclass

from ..experience.asset_consumer import DisplayResource
from ..experience.platform_adapter import AdapterConversionError, PlatformAdapter, PlatformPayload


class UnsupportedAstrBotResourceError(AdapterConversionError):
    """Raised when the AstrBot adapter cannot represent a resource type."""


class AstrBotPayloadBuildError(AdapterConversionError):
    """Raised when an AstrBot intermediate payload cannot be built."""


class InvalidPlatformPayloadError(AdapterConversionError):
    """Raised when a display resource lacks valid AstrBot payload fields."""


@dataclass(frozen=True)
class AstrBotImagePayload:
    """Transport-free intermediate representation of an AstrBot image resource."""

    type: str
    resource: str
    metadata: dict[str, str]

    @classmethod
    def from_display_resource(cls, resource: DisplayResource | None) -> "AstrBotImagePayload":
        """Build image payload metadata without opening, uploading, or sending a file."""
        if resource is None:
            raise InvalidPlatformPayloadError(
                "A display resource is required for AstrBot adaptation"
            )
        if resource.resource_type != "image":
            raise UnsupportedAstrBotResourceError(
                f"Unsupported AstrBot resource type: {resource.resource_type}"
            )
        if not isinstance(resource.path, str) or not resource.path:
            raise InvalidPlatformPayloadError("An AstrBot image resource reference is required")
        if not isinstance(resource.format, str) or resource.format.lower() != "png":
            raise InvalidPlatformPayloadError("An AstrBot image payload requires PNG format")
        if not isinstance(resource.metadata, dict):
            raise AstrBotPayloadBuildError("AstrBot payload metadata must be a dictionary")

        return cls(type="image", resource=resource.path, metadata=dict(resource.metadata))

    def as_platform_payload(self) -> PlatformPayload:
        """Expose this intermediate model through the stable generic adapter contract."""
        return PlatformPayload(
            payload_type=self.type,
            content=self.resource,
            metadata={"target_platform": "astrbot", "format": "png", **self.metadata},
        )


class AstrBotAdapter(PlatformAdapter):
    """Adapt generic display metadata to an AstrBot payload description only."""

    def adapt(self, resource: DisplayResource) -> PlatformPayload:
        """Return transport-free payload metadata; runtime delivery stays out of scope."""
        return AstrBotImagePayload.from_display_resource(resource).as_platform_payload()
