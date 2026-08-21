"""Abstract, storage-independent contract for reading deck manifests."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import DeckManifest


class DeckManifestProvider(ABC):
    """Provide immutable deck manifests without prescribing their storage."""

    @abstractmethod
    def get_manifest(self, deck_id: str) -> DeckManifest:
        """Return the manifest for ``deck_id`` or raise ``ManifestNotFoundError``."""
        raise NotImplementedError
