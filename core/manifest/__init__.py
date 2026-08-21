"""Storage-agnostic, read-only deck manifest provider contracts."""

from .errors import InvalidManifestError, ManifestNotFoundError
from .interface import DeckManifestProvider
from .models import AssetEntry, DeckManifest

__all__ = [
    "AssetEntry",
    "DeckManifest",
    "DeckManifestProvider",
    "InvalidManifestError",
    "ManifestNotFoundError",
]
