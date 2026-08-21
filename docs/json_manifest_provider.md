# JSON Manifest Provider

## Overview

`JSONManifestProvider` is the first concrete implementation of the read-only
`DeckManifestProvider` interface. It reads a package-local
`deck_metadata.json`, validates its metadata and asset paths, and returns an
immutable `DeckManifest` for future resolver use.

The provider dynamically addresses a deck by `deck_id`; it does not contain a
branch for Dark Cosmic Archive or any other fixed deck. Its root directory is
provided at construction time, allowing later packaged decks to use the same
implementation.

## Loading Flow

```text
deck_id
  -> <manifest_root>/<deck_id>/deck_metadata.json
  -> JSON validation
  -> DeckManifest
  -> tuple[AssetEntry, ...]
```

The existing archive manifest uses these legacy fields:

| Existing field | Returned contract field |
| --- | --- |
| `visual_deck_id` | `DeckManifest.deck_id` |
| `display_name` | `DeckManifest.name` |
| `specification_version` | `DeckManifest.version` |
| `status` | `DeckManifest.status` |
| `approved_major_assets` + `approved_minor_assets` | `DeckManifest.assets` |

Each resource becomes an `AssetEntry(card_id, asset_key, path, format)`. Minor
entries retain their recorded `asset_key`. The historical Major entries do not
have one, so the provider derives a stable key from the manifest `deck_id`,
`card_id`, and version. This conversion is in memory only and does not modify
`deck_metadata.json`.

## Implementation Boundary

The provider is responsible for locating a manifest relative to its configured
root, reading JSON, validating the manifest structure, validating asset paths,
and producing immutable data models.

It does not select a card, implement `AssetResolver`, open or transmit images,
send messages, make an AstrBot/QQ call, call an LLM, access user data, modify
the manifest, or write asset files.

## Error Handling

| Error | Trigger |
| --- | --- |
| `ManifestNotFoundError` | The deck identifier is unsafe or no manifest file exists at its package-local location. |
| `InvalidManifestError` | JSON syntax is invalid; a required field is missing; an asset list is invalid; identities duplicate; or an asset path is unsafe. |

Accepted asset paths are non-empty, package-relative POSIX paths ending in
`.png`. Absolute paths, Windows separators, directory traversal, and non-PNG
suffixes are rejected before any image is opened.

## Future Extension

`JSONManifestProvider` implements the stable `DeckManifestProvider` contract;
it does not alter that abstraction. Future SQLite, Remote, and Plugin Package
providers can return the same immutable `DeckManifest` and `AssetEntry` models
without changing `AssetResolver`'s future composition boundary.

This provider is intentionally a local, read-only manifest adapter. Deck
installation, remote fetching, caching, user-deck management, and a concrete
asset resolver remain separately scoped work.
