"""Default metadata-only implementation of the asset resolver contract."""

from __future__ import annotations

from ..manifest.errors import ManifestNotFoundError
from ..manifest.interface import DeckManifestProvider
from ..manifest.models import AssetEntry, DeckManifest
from .errors import AssetNotFoundError, DeckNotFoundError, InvalidAssetReferenceError
from .interface import AssetResolver
from .models import AssetReference


class DefaultAssetResolver(AssetResolver):
    """Resolve a logical card identity through an injected manifest provider."""

    def __init__(self, manifest_provider: DeckManifestProvider) -> None:
        self._manifest_provider = manifest_provider

    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        """Return a deck-specific resource reference for a logical card identity."""
        try:
            manifest = self._manifest_provider.get_manifest(deck_id)
        except ManifestNotFoundError as error:
            raise DeckNotFoundError(deck_id) from error

        entry = next((item for item in manifest.assets if item.card_id == card_id), None)
        if entry is None:
            raise AssetNotFoundError(deck_id, card_id)
        return self._to_reference(deck_id, manifest, entry)

    @staticmethod
    def _to_reference(
        deck_id: str, manifest: DeckManifest, entry: AssetEntry
    ) -> AssetReference:
        if not isinstance(entry.asset_key, str) or not entry.asset_key:
            raise InvalidAssetReferenceError(
                f"Asset for deck '{deck_id}' and card '{entry.card_id}' has an invalid asset_key"
            )
        if not isinstance(entry.format, str) or entry.format.lower() != "png":
            raise InvalidAssetReferenceError(
                f"Asset for deck '{deck_id}' and card '{entry.card_id}' has an invalid format"
            )
        if not isinstance(entry.path, str) or not entry.path.lower().endswith(".png"):
            raise InvalidAssetReferenceError(
                f"Asset for deck '{deck_id}' and card '{entry.card_id}' has an invalid path"
            )

        try:
            return AssetReference(
                deck_id=deck_id,
                card_id=entry.card_id,
                asset_key=entry.asset_key,
                path=entry.path,
                format=entry.format,
                version=manifest.version,
            )
        except InvalidAssetReferenceError as error:
            raise InvalidAssetReferenceError(
                f"Invalid asset reference for deck '{deck_id}' and card '{entry.card_id}'"
            ) from error
