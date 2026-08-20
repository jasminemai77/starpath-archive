# Dark Cosmic Archive visual specification

## Identity

- **Visual Deck ID:** `dark_cosmic_archive`
- **Display name:** Dark Cosmic Archive
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

## Asset boundary

Visual files remain under `assets/`. Tarot domain JSON and the Native Tool
contract do not embed image bytes and are unchanged by this visual Sprint.
