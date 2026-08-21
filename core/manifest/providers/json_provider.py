"""Read-only JSON implementation of the deck manifest provider contract."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from ..errors import InvalidManifestError, ManifestNotFoundError
from ..interface import DeckManifestProvider
from ..models import AssetEntry, DeckManifest

_DECK_ID_PATTERN = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*")
_MANIFEST_FILENAME = "deck_metadata.json"


class JSONManifestProvider(DeckManifestProvider):
    """Load a package-local JSON manifest without coupling to a deck identity."""

    def __init__(self, manifest_root: str | Path) -> None:
        self._manifest_root = Path(manifest_root)

    def get_manifest(self, deck_id: str) -> DeckManifest:
        """Load and validate ``deck_id`` from the provider's manifest root."""
        manifest_path = self._manifest_path(deck_id)
        if not manifest_path.is_file():
            raise ManifestNotFoundError(deck_id)

        try:
            with manifest_path.open(encoding="utf-8") as source:
                payload = json.load(source)
        except json.JSONDecodeError as error:
            raise InvalidManifestError(
                f"Invalid JSON manifest for '{deck_id}': {error.msg}"
            ) from error
        except OSError as error:
            raise InvalidManifestError(f"Cannot read manifest for '{deck_id}'") from error

        return self._to_manifest(payload, requested_deck_id=deck_id)

    def _manifest_path(self, deck_id: str) -> Path:
        if not isinstance(deck_id, str) or not _DECK_ID_PATTERN.fullmatch(deck_id):
            raise ManifestNotFoundError(deck_id)
        return self._manifest_root / deck_id / _MANIFEST_FILENAME

    @classmethod
    def _to_manifest(cls, payload: object, requested_deck_id: str) -> DeckManifest:
        document = cls._mapping(payload, "manifest")
        deck_id = cls._required_string(document, "visual_deck_id", "manifest")
        if deck_id != requested_deck_id:
            raise InvalidManifestError(
                f"Manifest deck id '{deck_id}' does not match requested '{requested_deck_id}'"
            )

        name = cls._required_string(document, "display_name", "manifest")
        version = cls._required_string(document, "specification_version", "manifest")
        status = cls._required_string(document, "status", "manifest")
        assets = cls._assets(document, deck_id=deck_id, version=version)

        return DeckManifest(
            deck_id=deck_id,
            name=name,
            version=version,
            status=status,
            assets=assets,
        )

    @classmethod
    def _assets(
        cls, document: dict[str, Any], deck_id: str, version: str
    ) -> tuple[AssetEntry, ...]:
        raw_assets = cls._asset_lists(document)
        entries = tuple(
            cls._to_asset_entry(raw, deck_id=deck_id, version=version, index=index)
            for index, raw in enumerate(raw_assets)
        )
        if not entries:
            raise InvalidManifestError("Manifest must contain at least one asset")
        if len({entry.card_id for entry in entries}) != len(entries):
            raise InvalidManifestError("Manifest contains duplicate card_id values")
        if len({entry.asset_key for entry in entries}) != len(entries):
            raise InvalidManifestError("Manifest contains duplicate asset_key values")
        return entries

    @classmethod
    def _asset_lists(cls, document: dict[str, Any]) -> list[object]:
        if "assets" in document:
            return cls._asset_list(document["assets"], "assets")

        major = cls._asset_list(document.get("approved_major_assets"), "approved_major_assets")
        minor = cls._asset_list(document.get("approved_minor_assets"), "approved_minor_assets")
        return [*major, *minor]

    @classmethod
    def _asset_list(cls, value: object, field_name: str) -> list[object]:
        if not isinstance(value, list):
            raise InvalidManifestError(f"Manifest field '{field_name}' must be a list")
        return value

    @classmethod
    def _to_asset_entry(
        cls, raw: object, deck_id: str, version: str, index: int
    ) -> AssetEntry:
        asset = cls._mapping(raw, f"asset at index {index}")
        card_id = cls._required_string(asset, "card_id", f"asset at index {index}")
        path = cls._safe_png_path(asset, index)
        asset_key = asset.get("asset_key")
        if asset_key is None:
            asset_key = cls._derived_asset_key(deck_id, card_id, version)
        if not isinstance(asset_key, str) or not asset_key:
            raise InvalidManifestError(f"Asset at index {index} has invalid asset_key")

        return AssetEntry(card_id=card_id, asset_key=asset_key, path=path, format="png")

    @staticmethod
    def _derived_asset_key(deck_id: str, card_id: str, version: str) -> str:
        normalized_card_id = card_id.replace("-", "_")
        normalized_version = version.replace(".", "_")
        return f"{deck_id}_{normalized_card_id}_v{normalized_version}"

    @staticmethod
    def _safe_png_path(asset: dict[str, Any], index: int) -> str:
        path = asset.get("path")
        if not isinstance(path, str) or not path:
            raise InvalidManifestError(f"Asset at index {index} has an empty or invalid path")
        parsed_path = PurePosixPath(path)
        if (
            parsed_path.is_absolute()
            or ".." in parsed_path.parts
            or "\\" in path
            or parsed_path.suffix.lower() != ".png"
        ):
            raise InvalidManifestError(
                f"Asset at index {index} must have a package-relative PNG path"
            )
        return path

    @staticmethod
    def _mapping(value: object, location: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise InvalidManifestError(f"{location.capitalize()} must be an object")
        return value

    @staticmethod
    def _required_string(document: dict[str, Any], field_name: str, location: str) -> str:
        value = document.get(field_name)
        if not isinstance(value, str) or not value:
            raise InvalidManifestError(f"{location.capitalize()} requires '{field_name}'")
        return value
