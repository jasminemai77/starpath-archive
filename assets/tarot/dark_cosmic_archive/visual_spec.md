# Dark Cosmic Archive visual specification

## Identity

- **Visual Deck ID:** `dark_cosmic_archive`
- **Display name:** Dark Cosmic Archive
- **Specification version:** `1.0`
- **Status:** frozen five-card visual baseline; further Major Arcana work must
  use this specification as its visual contract.
- **Scope:** the first complete 78-card visual theme for Starpath Archive. It
  is a deck-wide art direction, not a card back. This Sprint does not implement
  deck selection, switching, or additional visual themes.

## Worldview

Deep-space astronomy, ancient tarot symbolism, and a preserved celestial
archive. The mood is mysterious, old, quiet, and premium—not horror, neon
cyberpunk, anime, generic game UI, or a busy fantasy poster.

## Fixed visual system

| Element | Specification |
| --- | --- |
| Card ratio | 2:3 vertical |
| Palette | Deep space navy; muted nebula violet; aged antique gold; ivory white |
| Border | Restrained antique-gold double line; sparse star-map/orbit accents only |
| Number | Roman numeral, centered in a dedicated top title zone |
| English name | Uppercase serif, centered in the bottom title zone |
| Chinese name | Centered under the English name; high-contrast and readable |
| Typography | Fix title tracking/letter spacing across every card; no descriptive body copy |
| Fixed whitespace | Preserve the top numeral zone and a consistent bottom title zone; do not crowd the border |
| Main composition | One clear symbolic subject, a calm readable silhouette, and controlled celestial depth |

### Long Title Typography Rule

All English card titles use the same uppercase serif family, centered placement,
and fixed visual hierarchy. For titles wider than the standard title zone (for
example, **THE HIGH PRIESTESS**), reduce type size before changing letter
spacing; retain the deck-wide tracking value and preserve the fixed bottom
whitespace. Never wrap an English card title, compress it horizontally, or
allow it to collide with the border or Chinese title.

### Border Decoration Variation Rule

The antique-gold double border is fixed across the deck. Individual cards may
vary their sparse star-map, orbit, and constellation motifs to reflect their
symbolism, but the variation must remain subordinate to the border: retain
clear corners, preserve the approximately 10–15% reduced decoration density,
and avoid adding ornamental clusters on every side. The result should read as
one archival card system rather than five identical frames or unrelated frames.

## The Star — visual master

The approved **XVII — THE STAR / 星星** card is the visual master for the
deck. It defines the baseline treatment of a feminine symbolic figure, luminous
water, an eight-pointed guiding star, restrained gold linework, deep-blue field,
and bottom-title hierarchy.

Formal asset:

```text
major/17_the_star.png
```

Reference asset:

```text
reference/the_star_approved_v1.png
```

Both files are intentionally identical copies of the approved original. SHA-256:

```text
3B3C2B92BFB16CBEDFA42E0413CCA4D3231643978AEABFDF2F04B347A8CF2956
```

## Approved refinement constraints

Apply these to all future cards, including any future revision of The Star:

1. Reduce corner star-chart decoration by approximately 10–15%.
2. Fix title letter spacing rather than letting it vary by card.
3. Fix the bottom title-zone whitespace.
4. Fix the primary-star position for comparable celestial compositions.

## Reproducibility record

- Source: approved built-in image-generation prototype from this project task.
- Original generated file: `exec-3a5af0f1-9673-436d-b94b-b9349cf3589c.png`.
- Seed, model identifier, resolution controls, and raw generation settings were
  not exposed by the generation system and are therefore unavailable.
- The approved image is preserved unchanged; no substitute image was generated
during assetization.

## Frozen five-card baseline

The following assets are human-approved and establish the first deck-level
consistency baseline:

| Card | Formal asset |
| --- | --- |
| 0 — The Fool / 愚人 | `major/00_the_fool.png` |
| I — The Magician / 魔术师 | `major/01_the_magician.png` |
| II — The High Priestess / 女祭司 | `major/02_high_priestess.png` |
| III — The Empress / 皇后 | `major/03_empress.png` |
| IV — The Emperor / 皇帝 | `major/04_emperor.png` |
| V — The Hierophant / 教皇 | `major/05_hierophant.png` |
| VI — The Lovers / 恋人 | `major/06_lovers.png` |
| X — Wheel of Fortune / 命运之轮 | `major/10_wheel_of_fortune.png` |
| XIII — Death / 死神 | `major/13_death.png` |
| XVII — The Star / 星星 | `major/17_the_star.png` |
| XVIII — The Moon / 月亮 | `major/18_the_moon.png` |

Candidate history remains in `candidates/`; promotion to `major/` is a copy,
not a move. Do not replace the approved The Star visual master.

## Asset boundary

Visual files remain under `assets/`. Tarot domain JSON and the Native Tool
contract do not embed image bytes and are unchanged by this visual Sprint.
