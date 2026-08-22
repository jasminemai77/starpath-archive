"""Application-level composition for a user-triggered native image smoke test."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..core.manifest.providers import JSONManifestProvider
from ..core.resolver import AssetReference, DefaultAssetResolver
from ..experience.asset_consumer import DefaultAssetReferenceConsumer, DisplayResource
from ..experience.delivery import LocalRuntimeImageDelivery, PreparedAstrBotResource
from .astrbot_platform import AstrBotAdapter, AstrBotImagePayload

# Development smoke default only. Card selection still comes from the live manifest.
SMOKE_DEFAULT_DECK_ID = "dark_cosmic_archive"


@dataclass(frozen=True)
class NativeImageSmokePreparation:
    """Traceable outcome of the metadata-to-local-file preparation chain."""

    asset_reference: AssetReference
    display_resource: DisplayResource
    payload: AstrBotImagePayload
    prepared_resource: PreparedAstrBotResource


class NativeImageSmokeService:
    """Prepare one manifest-declared local PNG for a manual AstrBot smoke command."""

    def __init__(
        self,
        manifest_provider: JSONManifestProvider,
        resolver: DefaultAssetResolver,
        consumer: DefaultAssetReferenceConsumer,
        adapter: AstrBotAdapter,
        delivery: LocalRuntimeImageDelivery,
    ) -> None:
        self._manifest_provider = manifest_provider
        self._resolver = resolver
        self._consumer = consumer
        self._adapter = adapter
        self._delivery = delivery

    def prepare(self, deck_id: str = SMOKE_DEFAULT_DECK_ID) -> NativeImageSmokePreparation:
        """Resolve the first declared manifest asset through every production boundary."""
        manifest = self._manifest_provider.get_manifest(deck_id)
        card_id = manifest.assets[0].card_id
        asset_reference = self._resolver.resolve(deck_id, card_id)
        display_resource = self._consumer.consume(asset_reference)
        payload = self._adapter.build_image_payload(display_resource)
        prepared_resource = self._delivery.prepare(payload)
        return NativeImageSmokePreparation(
            asset_reference=asset_reference,
            display_resource=display_resource,
            payload=payload,
            prepared_resource=prepared_resource,
        )


def build_native_image_smoke_service() -> NativeImageSmokeService:
    """Compose the package-local manifest, resolver, and delivery boundaries."""
    package_root = Path(__file__).resolve().parents[1]
    tarot_root = package_root / "assets" / "tarot"
    manifest_provider = JSONManifestProvider(tarot_root)
    return NativeImageSmokeService(
        manifest_provider=manifest_provider,
        resolver=DefaultAssetResolver(manifest_provider),
        consumer=DefaultAssetReferenceConsumer(),
        adapter=AstrBotAdapter(),
        delivery=LocalRuntimeImageDelivery(tarot_root / SMOKE_DEFAULT_DECK_ID),
    )
