# Deck Resolver Interface Design

## 1. Overview

Starpath Archive already has a frozen 78-card visual deck and a future deck
metadata schema. It still needs an abstraction between a logical Tarot
`card_id` and a deck-specific visual resource. The Deck Resolver interface is
that resource-location boundary:

```text
card_id -> Deck Resolver -> AssetReference -> Experience Layer
```

This Sprint defines data contracts and abstract interfaces only. It does not
load `deck_metadata.json`, resolve the Dark Cosmic Archive, read an image, or
change runtime behaviour.

## 2. Architecture Boundary

The resolver is responsible for locating metadata:

- `DeckResolver` identifies a visual deck by `deck_id`.
- `AssetResolver` identifies an asset reference by `deck_id` and `card_id`.
- Returned data is a metadata-only `AssetReference`, not image bytes or a
  path string alone.

The resolver is not responsible for image loading or sending, message sending,
QQ/AstrBot adaptation, LLM calls, final reply generation, user interaction,
or user-data access. It is deliberately independent of a JSON file, a local
directory layout, and the Dark Cosmic Archive implementation.

## 3. DeckResolver Interface

```python
class DeckResolver(ABC):
    def get_deck(self, deck_id: str) -> DeckMetadata:
        ...
```

`get_deck` returns the deck-level descriptor for a supplied identifier. An
implementation must raise `DeckNotFoundError(deck_id)` when the requested deck
is unavailable; it must never return `None` silently.

## 4. AssetResolver Interface

```python
class AssetResolver(ABC):
    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        ...
```

`resolve` maps a stable logical Tarot identity to the selected deck's visual
resource. A future implementation may use a packaged manifest, an
administrator-installed deck, or a third-party deck package, but the interface
itself does not select a storage mechanism.

When the deck is unknown, an implementation raises `DeckNotFoundError`. When
the deck exists but does not provide the requested card, it raises
`AssetNotFoundError(deck_id, card_id)`. It never returns image content or a
bare string path.

## 5. Data Models

`DeckMetadata` is the minimal deck-level contract:

```python
DeckMetadata(
    deck_id="dark_cosmic_archive",
    name="Dark Cosmic Archive",
    version="1.0.0",
    status="approved",
)
```

`AssetReference` is an immutable resource reference:

```python
AssetReference(
    deck_id="dark_cosmic_archive",
    card_id="cups_05_five",
    asset_key="dark_cosmic_cups_05_v1",
    path="minor/cups/cups_05_five.png",
    format="png",
    version="1.0.0",
    resolution="1024x1536",
)
```

The required fields are `deck_id`, `card_id`, `asset_key`, `path`, and
`format`. `version` and `resolution` are optional extension fields. The model
accepts only a non-empty, package-relative POSIX path; absolute paths,
directory traversal, and Windows separators raise
`InvalidAssetReferenceError`.

`card_id` identifies the logical Tarot card and must not contain a filename.
`asset_key` identifies the deck-specific versioned resource. For example, the
same `major_17_star` identity can map to a Dark Cosmic Archive asset and a
future Nebula Dream asset without changing the Tarot Domain identity.

## 6. Error Handling

| Error | Condition | Locating information |
| --- | --- | --- |
| `DeckNotFoundError` | Requested deck is unavailable. | `deck_id` |
| `AssetNotFoundError` | Deck exists but has no requested card resource. | `deck_id`, `card_id` |
| `InvalidAssetReferenceError` | Returned reference is unsafe or incomplete. | Validation message |

All resolver errors derive from `ResolverError`. Explicit exceptions keep the
boundary observable and testable; they are preferable to a silent `None` or an
unstructured `ValueError`.

## 7. Multi Deck Extension

Both interfaces require `deck_id`, so no visual theme is hard-coded. The same
logical card can resolve differently for future deck IDs such as
`dark_cosmic_archive`, `nebula_dream`, or `custom_user_deck`.

The future metadata protocol supplies version and lifecycle information; a
future resolver may use those fields to choose an approved and enabled deck
version. This Sprint intentionally implements neither selection policy nor a
deck installation mechanism.

## 8. Compatibility Notes

The new `core.resolver` package is an isolated interface boundary. It does not
read the existing asset archive or its metadata and does not change:

- Tarot Domain identities or data files.
- The Native Tool Contract or structured tool result.
- Runtime integration, message behaviour, or Agent permissions.
- Existing PNG assets and candidate history.

`deck_metadata.json` remains the frozen Dark Cosmic Archive archive manifest.
The future metadata schema can later provide a concrete resolver implementation
without changing this interface contract.
