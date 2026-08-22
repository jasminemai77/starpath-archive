"""Platform-neutral contracts for consuming resolved visual asset metadata."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..core.resolver.models import AssetReference


class AssetReferenceMissingError(ValueError):
    """Raised when a display conversion receives no asset reference."""


class UnsupportedDisplayResourceError(ValueError):
    """Raised when a consumer cannot represent an asset reference format."""


class DisplayResourceUnavailableError(ValueError):
    """Reserved for a future presentation adapter that cannot access a resource."""


@dataclass(frozen=True)
class DisplayResource:
    """Platform-neutral metadata needed by a future presentation adapter."""

    resource_type: str
    path: str
    format: str
    metadata: dict[str, str]

    @classmethod
    def from_asset_reference(cls, asset_reference: AssetReference | None) -> "DisplayResource":
        """Convert validated resource metadata without opening or sending an asset."""
        if asset_reference is None:
            raise AssetReferenceMissingError(
                "An asset reference is required for display conversion"
            )
        if asset_reference.format.lower() != "png":
            raise UnsupportedDisplayResourceError(
                f"Unsupported display resource format: {asset_reference.format}"
            )

        metadata = {
            "deck_id": asset_reference.deck_id,
            "card_id": asset_reference.card_id,
            "asset_key": asset_reference.asset_key,
        }
        if asset_reference.version is not None:
            metadata["version"] = asset_reference.version
        if asset_reference.resolution is not None:
            metadata["resolution"] = asset_reference.resolution

        return cls(
            resource_type="image",
            path=asset_reference.path,
            format=asset_reference.format,
            metadata=metadata,
        )


class AssetReferenceConsumer(ABC):
    """Turn an asset reference into a platform-neutral display resource."""

    @abstractmethod
    def consume(self, asset_reference: AssetReference) -> DisplayResource:
        """Return a display description or raise an explicit conversion error."""
        raise NotImplementedError


class DefaultAssetReferenceConsumer(AssetReferenceConsumer):
    """Default metadata-only consumer used by platform integration boundaries."""

    def consume(self, asset_reference: AssetReference) -> DisplayResource:
        """Convert a resolved reference without opening or delivering its file."""
        return DisplayResource.from_asset_reference(asset_reference)
