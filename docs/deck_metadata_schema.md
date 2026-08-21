# Deck Metadata Schema

## 1. Overview

`deck_metadata.json` is sufficient for the frozen, single-deck Dark Cosmic
Archive v1.0 asset archive. Its entries combine a card identity, a relative
file path, and candidate provenance in one document. That shape is clear for a
fixed local collection, but it cannot unambiguously model several visual decks
for one Tarot card, independent deck releases, or a third-party deck package.

This document defines the **future metadata protocol** for visual decks. It is
a design baseline only: it does not replace the current metadata file, move an
asset, add a resolver, or change any runtime behaviour.

The intended relationship is:

```text
Deck -> Assets -> Cards
```

A deck is the first-class visual product. Its assets are versioned resources,
and each resource points to a stable logical Tarot card. Card identity never
depends on a filename or a particular deck.

## 2. Design Principles

### Deck First

A deck manifest describes one visual theme and its release. A card image is
not a standalone, ungrouped file: it belongs to a deck version and is listed
by that deck's manifest.

### Identity Separation

`card_id` identifies the logical Tarot card; it is stable across all visual
themes. `asset_key` identifies one visual resource supplied by one deck
release. Paths are storage details and must not be encoded into `card_id`.

For example, `major_17_star` can map to both a Dark Cosmic Archive image and a
future Nebula Dream image. Replacing one image creates a new `asset_key` or
asset version; it does not rename the logical card.

### Versioning

Every published deck manifest declares a version. An approved version is an
immutable record of its declared asset mappings and checksums. A visual change
is published as a new deck version rather than silently overwriting a frozen
manifest.

### Extensibility

The protocol leaves room for first-party, administrator-installed, user-owned,
and third-party visual decks. Extensions stay metadata-only and package-local;
they do not require changes to the Tarot Domain or the Native Tool contract.

## 3. Deck Schema

Each deck manifest has one `deck` object. The following minimum fields are
required:

```json
{
  "schema_version": "1.0",
  "deck_id": "dark_cosmic_archive",
  "name": "Dark Cosmic Archive",
  "version": "1.0.0",
  "author": "Starpath Archive contributors",
  "type": "visual_deck",
  "status": "approved"
}
```

| Field | Meaning |
| --- | --- |
| `schema_version` | Version of this metadata protocol, independent from the deck artwork version. |
| `deck_id` | Stable, lowercase, namespaced deck identifier; it must not contain an asset filename or a user secret. |
| `name` | Human-readable deck name. |
| `version` | Deck release version, using semantic versioning where practical (for example `1.0.0`). |
| `author` | Public creator or organization attribution. |
| `type` | Deck category. This protocol defines `visual_deck`. |
| `status` | Lifecycle state of the deck manifest; see [Status Lifecycle](#7-status-lifecycle). |

Recommended optional fields are `description`, `license`, `created_at`,
`updated_at`, `asset_root`, `card_count`, `source`, `extends`, and
`compatibility`. `extends` may declare an intentional derivative relationship;
it does not copy another deck's assets implicitly.

A complete future manifest can contain the deck descriptor, an asset inventory,
and card mappings:

```json
{
  "schema_version": "1.0",
  "deck": {
    "deck_id": "dark_cosmic_archive",
    "name": "Dark Cosmic Archive",
    "version": "1.0.0",
    "author": "Starpath Archive contributors",
    "type": "visual_deck",
    "status": "approved"
  },
  "assets": [],
  "card_mappings": []
}
```

## 4. Asset Schema

An asset object describes one visual file. It belongs to the enclosing deck
manifest and may be referenced by one or more declared presentation roles.

```json
{
  "asset_key": "dark_cosmic_major_17_star_v1",
  "card_id": "major_17_star",
  "type": "image",
  "path": "major/17_the_star.png",
  "format": "png",
  "resolution": "1024x1536",
  "status": "approved"
}
```

| Field | Meaning |
| --- | --- |
| `asset_key` | Unique resource identifier within the deck version. It is deck-specific and versioned. |
| `card_id` | Stable logical Tarot identity represented by this resource. |
| `type` | Asset media type. This protocol currently defines `image`. |
| `path` | Relative path inside the installed deck package. It must not be an absolute path or contain `..`. |
| `format` | Declared file format, currently `png` for the existing visual archive. |
| `resolution` | Pixel dimensions in `WIDTHxHEIGHT` form, such as `1024x1536`. |
| `status` | Lifecycle state of this individual resource. |

Recommended fields are `sha256`, `role` (for example `front`), `mime_type`,
`aspect_ratio`, `source_candidate`, `created_at`, `replaces`, and
`localizations`. `sha256` is strongly recommended for an approved or installed
asset so a package check can detect accidental replacement. The manifest must
store references and hashes only—never image binary data in JSON.

## 5. Card Mapping

`card_mappings` makes the deck-to-card selection explicit. It keeps a logical
card independent from the particular asset that a deck supplies for it.

```json
{
  "card_id": "major_17_star",
  "asset_key": "dark_cosmic_star_v1"
}
```

The pair must reference a known logical `card_id` and an asset in the same deck
manifest whose `card_id` matches. For a standard front-face deck, each logical
card has exactly one enabled `front` mapping per deck version. Alternative
resources such as localized title artwork may use a distinct `role`; they must
not replace the base card identity.

The logical card registry is owned by the Tarot Domain. This document does not
define, rename, or migrate its identifiers. A future resolver can use the
mapping as a read-only lookup:

```text
input: deck_id + optional deck version + card_id
output: matching approved/enabled asset metadata
```

That resolver is deliberately out of scope for this schema-design Sprint.

## 6. Versioning

A deck release is addressed as `deck_id@version`, for example
`dark_cosmic_archive@1.0.0`. `schema_version` and `version` have different
purposes:

- `schema_version` changes only when this metadata protocol changes.
- `version` changes when a deck release changes.

Recommended release rules:

- Patch version: metadata correction that does not change an approved image.
- Minor version: additive, backward-compatible visual resources or metadata.
- Major version: an incompatible mapping change, a changed approved asset, or
  a materially new visual baseline.

Once a deck version is approved, preserve its manifest and asset hashes. A
subsequent variant should identify `replaces` or `supersedes` explicitly rather
than altering the previous approved asset in place.

## 7. Status Lifecycle

The protocol uses explicit status values for both deck manifests and assets:

```text
candidate -> approved -> installed -> enabled
                         |              |
                         v              v
                      disabled <--- deprecated
```

| Status | Meaning |
| --- | --- |
| `candidate` | Present for review and not selectable as a formal deck resource. |
| `approved` | Human-approved manifest or resource, but not necessarily installed in a runtime. |
| `installed` | Available in a local installation, but not selected for use. |
| `enabled` | Installed and eligible for future resolver selection. |
| `disabled` | Retained but intentionally not selectable. |
| `deprecated` | Retained for compatibility; new selections should use a later replacement. |

Status does not imply predictive, user-profile, or chat behaviour. It only
describes asset availability and lifecycle.

## 8. Custom Deck Extension

Future custom and third-party packages use the same schema, a globally
distinct `deck_id`, public ownership metadata, and package-local relative
paths. For example:

```json
{
  "schema_version": "1.0",
  "deck_id": "user_custom_example",
  "name": "Example Custom Deck",
  "version": "0.1.0",
  "author": "Example creator",
  "owner": "user",
  "type": "visual_deck",
  "status": "candidate"
}
```

`owner` is an extension field with values such as `first_party`, `user`,
`administrator`, or `third_party`. A future installer may add non-sensitive
provenance such as `package_id`, `publisher`, `license`, `source_url`, and a
package checksum. It must not place passwords, API keys, tokens, chat history,
or user-profile data in deck metadata.

This design accommodates user uploads, plugin-market packages, administrator
installation, and third-party decks. It does not design their permissions,
database records, cloud synchronization, storefront, or UI.

## 9. Migration Strategy

The current
[`deck_metadata.json`](../assets/tarot/dark_cosmic_archive/deck_metadata.json)
remains the authoritative frozen archive during this design phase. A later,
separate migration may follow these steps:

1. Create a `1.0` protocol manifest for the existing Dark Cosmic Archive
   without moving or renaming any PNG.
2. Preserve the current root `visual_deck_id`, `display_name`, specification
   version, asset root, policy, and candidate provenance as deck-level and
   asset-level metadata.
3. Convert every registered formal entry into an explicit asset plus a
   `card_mapping`; calculate and record its SHA-256.
4. Retain the historical Major identifiers (`major-00` through `major-21`) and
   Minor identifiers as they are. If future canonical identifiers use the
   underscore form shown in this document, record aliases in a compatibility
   layer—do not silently change established Tarot identities.
5. Validate the 78 existing relative paths and publish the new manifest only
   after a dedicated migration review.

The existing root status, `approved_full_major_arcana`, is historically valid
for the point at which it was written. A future manifest should instead use
the explicit lifecycle status and `card_count` to represent the completed 78
card deck precisely.

## 10. Compatibility Notes

This is a documentation-only protocol baseline. It has no runtime effect and
does not change the following boundaries:

- Tarot Domain owns logical card identity and remains unchanged.
- Tool Contract remains structured-result-only and receives no visual-deck
  parameter in this Sprint.
- Runtime, AstrBot integration, Agent permissions, and message behaviour
  remain unchanged.

Future implementations must treat paths as package-local metadata, validate
format, resolution, uniqueness, card coverage, and checksums before enabling a
deck. They must preserve existing static-asset operation and introduce no
runtime image-generation dependency.

## Scope Boundary

This document intentionally does not specify a database, user-permission
model, cloud-sync service, marketplace/store system, UI management screen, or
Deck Resolver implementation. Those may consume this protocol in later,
separately approved work.
