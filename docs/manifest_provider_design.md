# Deck Manifest Provider Interface Design

## Overview

The Deck Resolver interface identifies a deck-specific visual resource for a
logical `card_id`. It must not decide where a deck manifest comes from. The
Deck Manifest Provider introduces that missing, read-only boundary:

```text
AssetResolver -> DeckManifestProvider -> DeckManifest -> AssetEntry
```

This Sprint provides the interface and immutable data contracts only. It does
not read `deck_metadata.json`, parse JSON, inspect asset files, or implement a
Dark Cosmic Archive provider.

## Responsibility Boundary

`DeckManifestProvider` is responsible only for returning a complete
`DeckManifest` identified by `deck_id`. It does not select a card, resolve an
asset, load an image, send a message, know an AstrBot platform, call an LLM,
or access user data.

`AssetResolver` remains responsible for mapping `deck_id` plus `card_id` to an
`AssetReference`. A future resolver implementation can obtain a manifest from
a provider, find the matching `AssetEntry`, and construct the reference. The
provider itself performs none of those resolver steps.

Both boundaries are storage independent and read-only. Neither interface
creates, updates, installs, or deletes a deck.

## Interface Definition

```python
class DeckManifestProvider(ABC):
    def get_manifest(self, deck_id: str) -> DeckManifest:
        ...
```

`get_manifest` accepts a deck identifier such as `dark_cosmic_archive` and
returns an immutable manifest snapshot. Implementations must raise
`ManifestNotFoundError(deck_id)` when the identifier is unavailable; they must
not silently return `None`.

The interface makes no assumption about JSON, local directories, a fixed deck,
or any other storage strategy.

## Data Models

`DeckManifest` is a frozen configuration snapshot:

```python
DeckManifest(
    deck_id="dark_cosmic_archive",
    name="Dark Cosmic Archive",
    version="1.0.0",
    status="approved",
    assets=(...),
)
```

It contains the required deck identity and lifecycle fields plus an immutable
tuple of `AssetEntry` records. Its `assets` collection is a tuple so that a
provider cannot expose a mutable manifest list at runtime.

`AssetEntry` describes the manifest-level mapping data:

```python
AssetEntry(
    card_id="major_17_star",
    asset_key="dark_cosmic_major_17_v1",
    path="major/17_the_star.png",
    format="png",
)
```

`card_id` remains the logical Tarot identity. `asset_key`, path, and format
describe the visual resource supplied by this particular deck. The entry holds
no personal information and contains no display or messaging logic.

## Error Handling

| Error | Condition | Locating information |
| --- | --- | --- |
| `ManifestNotFoundError` | No manifest exists for the requested deck. | `deck_id` |
| `InvalidManifestError` | A provider obtains data that cannot satisfy the manifest contract. | Validation message from a future provider. |

Both errors derive from `ManifestProviderError`. This keeps failure states
explicit and testable instead of returning `None` or a partially formed
manifest.

## Storage Extension

The same interface is intentionally suitable for later, separately approved
providers:

1. **JSON Provider** — reads a package-local manifest document.
2. **SQLite Provider** — reads a manifest snapshot from a local database.
3. **Remote Provider** — obtains a validated immutable manifest from a remote
   source.
4. **Plugin Package Provider** — exposes a manifest bundled in a third-party
   deck package.

None of these providers are implemented in this Sprint. Storage-specific
validation, package installation, remote access, and caching remain outside
this interface contract.

## Compatibility Notes

The `core.manifest` package does not use the current asset archive and has no
runtime integration. It does not change:

- Tarot Domain data or logical identities.
- Tool Contract or structured tool output.
- Runtime or AstrBot platform integration.
- Experience Layer responsibilities.
- Existing PNG assets, candidate history, or `deck_metadata.json`.

The provider contract is compatible with the existing Deck Metadata Schema and
Deck Resolver Interface Design. A later resolver implementation can compose
the two abstractions without changing their public method signatures.
