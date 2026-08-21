"""Explicit errors for the visual resource resolver boundary."""

from __future__ import annotations


class ResolverError(Exception):
    """Base error for deck metadata and visual asset resolution."""


class DeckNotFoundError(ResolverError):
    """Raised when a requested deck identifier is unavailable."""

    def __init__(self, deck_id: str) -> None:
        super().__init__(f"Deck not found: {deck_id}")
        self.deck_id = deck_id


class AssetNotFoundError(ResolverError):
    """Raised when a deck has no visual asset for a requested card."""

    def __init__(self, deck_id: str, card_id: str) -> None:
        super().__init__(f"Asset not found for deck '{deck_id}' and card '{card_id}'")
        self.deck_id = deck_id
        self.card_id = card_id


class InvalidAssetReferenceError(ResolverError):
    """Raised when an asset reference cannot safely describe a package asset."""
