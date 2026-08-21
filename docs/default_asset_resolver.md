# Default Asset Resolver

## Overview

`DefaultAssetResolver` is the first concrete implementation of the
`AssetResolver` contract. It maps a logical `card_id` in a supplied `deck_id`
to an immutable `AssetReference`. It returns resource metadata only; it never
loads an image or sends it.

## Architecture Position

The resolver sits between Tarot Domain card identity and the Experience Layer:

```text
card_id + deck_id
  -> DefaultAssetResolver
  -> AssetReference
  -> Experience Layer
```

It does not change Tarot Domain records, Tool Contract fields, Runtime
behaviour, or Experience Layer responsibilities.

## Resolve Flow

```text
deck_id + card_id
  -> DeckManifestProvider.get_manifest(deck_id)
  -> DeckManifest.assets
  -> matching AssetEntry.card_id
  -> AssetReference
```

The resolver performs one provider lookup per `resolve` call, selects a single
matching entry, and carries forward the caller's deck ID, entry identity,
resource key, relative path, format, and manifest version. It has no fixed
deck branch and therefore supports any provider-backed visual deck.

## Dependency Injection

The constructor accepts a `DeckManifestProvider` interface rather than a JSON
file or a concrete provider. `JSONManifestProvider` is one valid injected
implementation; later SQLite, Remote, or Plugin Package providers can be
substituted without changing the resolver interface or mapping logic.

The resolver never opens `deck_metadata.json`. Manifest location, parsing, and
validation remain the provider's responsibility.

## Error Handling

| Condition | Result |
| --- | --- |
| Provider cannot find the deck | `ManifestNotFoundError` is translated to `DeckNotFoundError` with exception chaining. |
| Manifest lacks the card | `AssetNotFoundError(deck_id, card_id)`. |
| Selected resource is empty, non-PNG, unsafe, or incomplete | `InvalidAssetReferenceError`. |

No lookup silently returns `None`, a bare path, or image content.

## Future Extension

Because `deck_id` is an input and the provider is injected, the same resolver
supports multiple and custom decks. The initial linear lookup is sufficient
for the current 78 assets and intentionally avoids a cache. A future cache or
dynamic-resource strategy can be introduced behind the provider/resolver
boundary after profiling and lifecycle invalidation rules are defined.

## Compatibility Notes

This implementation is metadata-only and does not modify or read visual image
content. It does not affect:

- Tarot Domain or its stable card identities.
- Tool Contract or message structure.
- Runtime, AstrBot integration, or Agent permissions.
- Experience Layer rendering or messaging.
- `deck_metadata.json`, PNG assets, or candidate history.

The current Dark Cosmic Archive manifest continues to use historical Major IDs
such as `major-17`; no canonical-ID aliasing is added by this resolver.
