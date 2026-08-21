# Dark Cosmic Archive v1.0 Visual Audit

## Summary

Audit date: 2026-08-21
Scope: the formal Dark Cosmic Archive assets and their visual metadata only.

**Final decision: PASS WITH NOTES.**

All 78 formal PNG assets are present, readable, correctly sized, and mapped to
their registered visual paths. No image, Tarot Domain record, Tool Contract,
runtime component, or Agent permission was changed by this audit.

## Asset Inventory

| Category | Count |
| --- | ---: |
| Major Arcana | 22 |
| Wands | 14 |
| Cups | 14 |
| Swords | 14 |
| Pentacles | 14 |
| **Total** | **78** |

Directory structure is present as specified:

- `major/` contains the continuous `00`–`21` Major Arcana sequence.
- `minor/wands/`, `minor/cups/`, `minor/swords/`, and `minor/pentacles/`
  each contain 14 formal assets.
- No duplicate formal filename or missing formal asset was found.

## File Integrity

- All 78 formal files are readable PNG images.
- All images are `1024 × 1536` pixels, preserving the required 2:3 ratio.
- File sizes range from 2,482,096 to 3,764,471 bytes; no anomalous empty or
  unreadable asset was found.
- A deterministic SHA-256 manifest was calculated over the sorted formal asset
  hashes and relative paths: `ba2cd113d2f7966e021dd0d70a4becf0121e854d23a06f57a96a44c676b7d7af`.

## Metadata Validation

- `deck_metadata.json` contains 22 approved Major entries and 56 approved
  Minor entries: 78 registered visual resources in total.
- No duplicate `card_id` was found.
- Every registered `path` resolves to an existing formal PNG.
- Formal Minor entries retain a stable `asset_key` identical to their
  deck-independent `card_id`.

### Metadata schema note

The existing, frozen metadata schema places deck-level identity and approval
state at the root (`visual_deck_id` and visual status), while individual asset
entries contain `card_id`, `asset_key`, suit/rank, title, path, and
`candidate_source`. It does not repeat per-entry `deck` and `status: approved`
fields. This is a documentation/schema-normalization follow-up only; it does
not create a broken mapping or affect formal asset resolution. No metadata
change was made in this audit-only Sprint.

## Card Mapping Validation

All 78 registered file paths resolve correctly. Minor Arcana mappings follow
the required stable identity pattern, for example:

```text
card_id: wands_01_ace
asset_key: wands_01_ace
path: minor/wands/wands_01_ace.png
```

No identity/resource-path mismatch was found. Major Arcana retain their
existing `major-XX` identity convention and continuous formal filenames.

## Visual Consistency Review

Visual review was performed against `visual_spec.md`,
`minor_arcana_visual_spec.md`, and `minor_arcana_generation_template.md`, with
representative checks of long-title Major cards and all four Minor suit
grammars.

- **Color system:** deep-space blue, muted nebula violet, antique gold, and
  ivory typography are consistently present.
- **Border system:** Major cards preserve the richer archive frame; Minor cards
  use compatible, visually lighter star-map/orbit decoration.
- **Typography:** top rank markers and fixed lower English/Chinese title bands
  are present and readable in reviewed assets. Long titles, including
  `THE HIGH PRIESTESS` and `WHEEL OF FORTUNE`, remain centered and unwrapped.
- **Lighting:** Major assets retain chapter-scale celestial focal light; Minor
  assets use calmer, stable focal illumination.
- **Wands:** communicate stellar energy trajectories rather than ordinary
  flame magic.
- **Cups:** use moonlit star-sea, vessel, reflection, and tide language rather
  than generic water scenes.
- **Swords:** use optical axes, star tracks, and spatial geometry rather than
  warfare or weapon combat.
- **Pentacles:** use crystal, gravity, lattice, and orbital material systems
  rather than coins, wealth, or luxury symbolism.

## Candidate History

Candidate history remains present under `candidates/`, including
`minor_batch_wands/`, `minor_batch_cups/`, `minor_batch_swords/`, and
`minor_batch_pentacles/`. This preserves source traceability for the formal
Minor Arcana assets.

## Issues Found

1. **Metadata schema normalization note (non-blocking):** per-entry `deck` and
   `status` are not repeated in the historical `deck_metadata.json` schema.
   Root-level deck identity and asset-list membership currently supply that
   context; normalize fields only in a future metadata-focused change.
2. No missing, duplicate, unreadable, incorrectly sized, or incorrectly mapped
   formal visual asset was found.

## Final Decision

**PASS WITH NOTES** — Dark Cosmic Archive v1.0 has a complete, intact 78-card
formal visual baseline and is ready for the next release-planning or
metadata-normalization decision. This audit does not create a software release
tag.
