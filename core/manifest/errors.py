"""Explicit errors for the read-only deck manifest provider boundary."""

from __future__ import annotations


class ManifestProviderError(Exception):
    """Base error for deck manifest provider operations."""


class ManifestNotFoundError(ManifestProviderError):
    """Raised when the provider does not contain the requested deck manifest."""

    def __init__(self, deck_id: str) -> None:
        super().__init__(f"Deck manifest not found: {deck_id}")
        self.deck_id = deck_id


class InvalidManifestError(ManifestProviderError):
    """Raised when manifest data cannot meet the declared contract."""
