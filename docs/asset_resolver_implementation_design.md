# AssetResolver Implementation Design

## Overview

The next implementation step is a concrete `DefaultAssetResolver`. It maps a
logical Tarot `card_id` to a deck-specific `AssetReference` while preserving
the existing separation between logical cards, deck manifests, and visual
resources.

This document is an implementation design and test plan only. It does not add
a resolver class, read a manifest, alter `deck_metadata.json`, or inspect an
image file.

## Architecture Position

The resolver belongs between the Tarot Domain identity and the Experience
Layer's metadata consumption:

```text
Tarot Domain (card_id)
  -> AssetResolver
  -> AssetReference
  -> Experience Layer
```

It is not an image service. It does not load, transmit, or render an asset, and
it does not generate a chat reply, interact with QQ/AstrBot, call an LLM, or
read personal data.

## Dependency Design

The concrete class should be placed at
`core/resolver/default_resolver.py` and implement the existing
`AssetResolver` abstract interface without changing that interface.

```python
class DefaultAssetResolver(AssetResolver):
    def __init__(self, manifest_provider: DeckManifestProvider) -> None:
        ...

    def resolve(self, deck_id: str, card_id: str) -> AssetReference:
        ...
```

The constructor accepts only the abstract `DeckManifestProvider`, never a JSON
path, an asset directory, or a `JSONManifestProvider` concrete type. This
allows the resolver to compose later with JSON, SQLite, Remote, or Plugin
Package providers without knowing their storage details.

```text
DefaultAssetResolver
  -> DeckManifestProvider.get_manifest(deck_id)
  -> DeckManifest.assets
  -> matching AssetEntry
  -> AssetReference
```

No `if deck_id == ...` branch is permitted. The resolver never opens
`deck_metadata.json`; only a manifest provider may do that.

## Resolve Flow

For input `deck_id` plus `card_id`, `resolve` should perform these steps:

1. Call `manifest_provider.get_manifest(deck_id)` exactly once.
2. Search that returned manifest's `assets` for the sole entry whose
   `AssetEntry.card_id` equals the supplied `card_id`.
3. If no matching entry exists, raise `AssetNotFoundError(deck_id, card_id)`.
4. Validate the selected entry while constructing an `AssetReference`.
5. Return an immutable reference containing the manifest's `deck_id`, the
   entry's `card_id`, `asset_key`, path, format, and `version=manifest.version`.

The resolver must preserve the deck identity in the returned reference: the
same logical card may resolve to a different resource in another deck.

Current Dark Cosmic Archive integration tests must use the IDs actually
present in its frozen manifest—for example `major-17` and `cups_05_five`.
`major_17_star` remains a future canonical-ID example from the metadata schema;
an alias registry is a separate migration concern and must not be silently
implemented by the resolver.

## Error Handling

| Situation | Source | Resolver-facing result |
| --- | --- | --- |
| Unknown deck | `DeckManifestProvider` raises `ManifestNotFoundError`. | Raise `DeckNotFoundError(deck_id)` from the provider exception to preserve the cause. |
| Known deck, unknown card | Resolver cannot find an `AssetEntry`. | Raise `AssetNotFoundError(deck_id, card_id)`. |
| Unsafe or incomplete selected entry | Conversion to `AssetReference` fails validation, or explicit key/format checks fail. | Raise `InvalidAssetReferenceError` with the deck/card context. |

The resolver must never return `None`, a bare string path, or image content.
It should not hide the provider exception: exception chaining makes a manifest
lookup failure diagnosable while retaining the resolver interface's
`DeckNotFoundError` contract.

Before creating an `AssetReference`, the implementation must reject empty
`asset_key` or `format` values. Existing `AssetReference` validation already
rejects empty required fields, absolute paths, backslash paths, and directory
traversal. Any additional asset-key syntax rule should be added only if it is
defined and approved in a dedicated model-validation change; the resolver must
not invent a deck-specific naming rule.

## Performance and Extension Strategy

The initial algorithm is a simple in-memory linear search of `DeckManifest`
assets. At 78 entries this is transparent and sufficient; at 780 entries it
remains easy to reason about. Do not add caching in the first implementation.

If profiling later proves a need, caching belongs behind the existing provider
or resolver construction boundary. It must preserve immutable manifest
snapshots, explicit lifecycle status, and clear invalidation rules. This design
already supports multiple decks and custom decks because `deck_id` is a method
input and the provider is abstract.

## Test Plan

The implementation Sprint should add focused tests using a small fake
`DeckManifestProvider`, plus an integration test composed with
`JSONManifestProvider`:

| Test | Expected result |
| --- | --- |
| Major single-card lookup | Resolve Dark Cosmic Archive `major-17`; retain deck ID, path, format, derived key, and manifest version. |
| Minor single-card lookup | Resolve `cups_05_five`; preserve its recorded `asset_key` and minor path. |
| Unknown card | Existing deck plus an unknown ID raises `AssetNotFoundError` carrying both identities. |
| Unknown deck | Provider's missing-manifest failure becomes `DeckNotFoundError`, with the original exception chained. |
| Invalid entry | Empty key, empty format, or unsafe path raises `InvalidAssetReferenceError`. |
| Full inventory | Every one of the 78 `card_id` values in the JSON-backed manifest resolves to an `AssetReference`. |
| Provider composition | The resolver calls `get_manifest` once and never reads files directly. |
| Boundary scan | Resolver source has no LLM, image/message sending, runtime integration, or personal-data dependency. |

The tests must not assert a fixed directory outside the provider. They should
assert only the returned metadata contract and explicit exception types.

## Compatibility Notes

This plan leaves all existing boundaries intact:

- Tarot Domain remains the source of logical card identity.
- Tool Contract stays unchanged and receives no resolver parameter in this
  stage.
- Runtime and Experience Layer continue to receive only structured metadata;
  neither becomes responsible for manifest storage.
- Existing PNGs, candidate history, and `deck_metadata.json` remain unchanged.

Implementing this plan later requires only a new concrete resolver and tests;
it does not require a new card deck, a card-selection feature, user-deck
management, or a caching system.
