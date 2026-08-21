"""Immutable data contracts for a visual deck manifest snapshot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetEntry:
    """One card-to-resource declaration contained by a deck manifest."""

    card_id: str
    asset_key: str
    path: str
    format: str


@dataclass(frozen=True)
class DeckManifest:
    """A complete, read-only visual deck metadata snapshot."""

    deck_id: str
    name: str
    version: str
    status: str
    assets: tuple[AssetEntry, ...]
