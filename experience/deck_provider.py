"""Small injected source for the visual deck context outside ``starpath.tool.v1``."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol


class DeckProvider(Protocol):
    """Provide the active visual deck without reading it from a tool result."""

    def get_default_deck_id(self) -> str:
        """Return the explicitly configured visual deck identifier."""


class MissingDefaultDeckError(ValueError):
    """Raised when runtime configuration has not selected a visual deck."""


class ConfigDeckProvider:
    """Adapt the existing plugin configuration mapping to ``DeckProvider``.

    This is deliberately a minimal adapter, not a new configuration schema. A
    deployment opts in by providing its existing ``default_deck_id`` value; the
    tool result remains free of visual-deck concerns.
    """

    def __init__(self, config: Mapping[str, Any] | None) -> None:
        self._config = config

    def get_default_deck_id(self) -> str:
        value = self._config.get("default_deck_id") if self._config else None
        if not isinstance(value, str) or not value.strip():
            raise MissingDefaultDeckError(
                "A runtime default_deck_id is required for experience capture"
            )
        return value


class PackageDeckProvider(ConfigDeckProvider):
    """Use existing config when present, otherwise the single packaged deck.

    The fallback makes the current single-deck installation usable without
    introducing a new runtime-config schema.  It intentionally fails as soon
    as more than one packaged deck is available and no existing configuration
    selects one, preserving the future deck-selection boundary.
    """

    def __init__(
        self,
        manifest_root: str | Path,
        config: Mapping[str, Any] | None,
    ) -> None:
        super().__init__(config)
        self._manifest_root = Path(manifest_root)

    def get_default_deck_id(self) -> str:
        try:
            return super().get_default_deck_id()
        except MissingDefaultDeckError:
            pass

        deck_ids = self._packaged_deck_ids()
        if len(deck_ids) != 1:
            raise MissingDefaultDeckError(
                "Runtime config must select a deck when packaged decks are not unique"
            )
        return deck_ids[0]

    def _packaged_deck_ids(self) -> tuple[str, ...]:
        if not self._manifest_root.is_dir():
            return ()

        deck_ids: list[str] = []
        for manifest_path in self._manifest_root.glob("*/deck_metadata.json"):
            try:
                with manifest_path.open(encoding="utf-8") as source:
                    manifest = json.load(source)
            except (OSError, json.JSONDecodeError):
                continue
            deck_id = manifest.get("visual_deck_id") if isinstance(manifest, dict) else None
            if isinstance(deck_id, str) and deck_id.strip():
                deck_ids.append(deck_id)
        return tuple(sorted(set(deck_ids)))
