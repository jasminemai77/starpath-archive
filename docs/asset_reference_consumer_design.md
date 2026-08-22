# AssetReference Consumer Design

## Overview

The Experience Layer needs a platform-neutral way to use the resource metadata
already located by `DefaultAssetResolver`. The AssetReference Consumer boundary
converts an `AssetReference` into a `DisplayResource` that a future sender,
API, Web view, or local UI can interpret.

This Sprint defines that contract and its pure metadata conversion only. It
does not send images, open files, perform platform adaptation, or change the
existing structured Tool Contract.

## Architecture Boundary

Resolver and Experience have separate responsibilities:

```text
card_id + deck_id
  -> AssetResolver
  -> AssetReference
  -> AssetReferenceConsumer
  -> DisplayResource
  -> future platform adapter
```

The resolver locates a resource and validates its package-relative reference.
The consumer transforms that reference into display metadata. Neither component
reads `deck_metadata.json`, searches by card identity, assembles file paths,
loads an image, or sends a message.

`DisplayResource` remains intentionally free of QQ, Telegram, Web, API, or UI
payload fields. A platform adapter belongs after this boundary.

## Consumer Interface

```python
class AssetReferenceConsumer(ABC):
    def consume(self, asset_reference: AssetReference) -> DisplayResource:
        ...
```

Implementations accept only an already-resolved `AssetReference`; they do not
depend on `AssetResolver`, `DeckManifestProvider`, a JSON file, or a deck ID.
The abstract interface is reserved for a future presentation policy. The
current `DisplayResource.from_asset_reference()` establishes the deterministic,
platform-neutral conversion contract without adding a sending implementation.

## Display Resource Model

```python
DisplayResource(
    resource_type="image",
    path="major/17_the_star.png",
    format="png",
    metadata={
        "deck_id": "dark_cosmic_archive",
        "card_id": "major-17",
        "asset_key": "dark_cosmic_archive_major_17_v1_0",
        "version": "1.0",
    },
)
```

| Field | Purpose |
| --- | --- |
| `resource_type` | Generic resource category; this visual contract produces `image`. |
| `path` | The validated package-relative path supplied by the resolver. |
| `format` | The source resource format, currently `png`. |
| `metadata` | Stable context needed by a future adapter: deck, card, asset key, and optional version/resolution. |

No image bytes, platform payload, message text, user identifier, or agent state
is represented by the model.

## Conversion Flow

1. Business logic has a logical `card_id` and a selected `deck_id`.
2. `AssetResolver` returns an `AssetReference`.
3. The consumer converts that reference to `DisplayResource` without I/O.
4. A future platform adapter may decide whether and how to access the resource.

The consumer preserves the resolver's path, format, deck identity, card
identity, and asset key. It never recomputes them.

## Error Handling

| Condition | Error | Boundary action |
| --- | --- | --- |
| No reference supplied | `AssetReferenceMissingError` | Fail conversion explicitly. |
| Unsupported format | `UnsupportedDisplayResourceError` | Fail before generating a display description. |
| Resource later cannot be accessed | `DisplayResourceUnavailableError` | Reserved for a future platform/presentation adapter; this consumer does not perform filesystem I/O. |
| Platform-specific conversion fails | Adapter-specific error | Remains outside this generic consumer contract. |

Failures never silently become an empty path, a missing image, or a generated
chat response.

## Multi Platform Extension

The same `DisplayResource` can be consumed by future QQ, Web, API, and local
UI adapters because it exposes only generic asset metadata. Platform modules
may create their own payload types after receiving this model; they must not
be added to the core consumer interface.

## Compatibility Notes

This is an isolated presentation-boundary contract. It does not change:

- Tarot Domain or card identity.
- Tool parameters, structured result fields, or Agent permissions.
- Runtime or QQ integration.
- Resolver or Manifest Provider interfaces and implementations.
- Existing visual assets or metadata files.

The existing `StarpathExperience` record organizer remains unchanged. No
`DisplayResource` is inserted into the current Tool result in this Sprint.
