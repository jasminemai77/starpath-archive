"""Abstract contracts for locating visual deck metadata and asset references."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import AssetReference, DeckMetadata


class DeckResolver(ABC):
    """Locate deck metadata without prescribing a source or storage format."""

    @abstractmethod
    def get_deck(self, deck_id: str) -> DeckMetadata:
        """Return metadata for ``deck_id`` or raise ``DeckNotFoundError``."""
        raise NotImplementedError


class AssetResolver(ABC):
    """Locate a deck-specific asset reference for a logical card identity."""

    @abstractmethod
    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        """Return an asset reference or raise a resolver-specific error."""
        raise NotImplementedError
