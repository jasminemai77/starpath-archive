"""Immutable data contracts for visual deck resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from .errors import InvalidAssetReferenceError


@dataclass(frozen=True)
class DeckMetadata:
    """Deck-level metadata independent of its storage or loading mechanism."""

    deck_id: str
    name: str
    version: str
    status: str


@dataclass(frozen=True)
class AssetReference:
    """A safe, metadata-only reference to one visual card resource."""

    deck_id: str
    card_id: str
    asset_key: str
    path: str
    format: str
    version: str | None = None
    resolution: str | None = None

    def __post_init__(self) -> None:
        required_fields = {
            "deck_id": self.deck_id,
            "card_id": self.card_id,
            "asset_key": self.asset_key,
            "path": self.path,
            "format": self.format,
        }
        empty_fields = [name for name, value in required_fields.items() if not value]
        if empty_fields:
            joined = ", ".join(empty_fields)
            raise InvalidAssetReferenceError(f"Asset reference has empty fields: {joined}")

        asset_path = PurePosixPath(self.path)
        if asset_path.is_absolute() or ".." in asset_path.parts or "\\" in self.path:
            raise InvalidAssetReferenceError(
                "Asset reference path must be package-relative and must not traverse directories"
            )
