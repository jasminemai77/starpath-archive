# Dark Cosmic Archive visual specification

## Identity

- **Visual Deck ID:** `dark_cosmic_archive`
- **Display name:** Dark Cosmic Archive
- **Specification version:** `1.0`
- **Status:** frozen v1.0 visual contract; all 22 Major Arcana assets are
  human-approved and further visual work must use this specification as its
  visual contract.
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

### Color System

Deep space navy is the dominant field, supported by low-saturation nebula
violet. Aged antique gold is reserved for structural linework, celestial
highlights, and restrained focal accents; ivory white provides readable
typography and high-value starlight. Individual card symbolism may alter the
balance of these colors, but must not replace the deck's dark cosmic base with
an oversaturated or flat color field.

### Border System

Every card retains the restrained antique-gold double-line archive frame with
sparse star-map and orbit accents. The border establishes a stable visual
weight, leaves the title zones clear, and remains subordinate to the card's
central symbolic subject.

### Typography Rule

Use a centered Roman numeral in the dedicated top zone, then a centered
uppercase English title and Chinese title in the fixed bottom zone. Preserve
the deck-wide serif hierarchy, tracking, contrast, and whitespace; never add
descriptive copy to a card face.

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

### Lighting Rule

Use one coherent ancient celestial illumination per card: a calm, readable
focal light supported by subtle antique-gold highlights against deep-space
shadow. Light may become stronger for card-specific events, but must remain
painterly and archival rather than neon, UI-like, photographic, or theatrical
poster lighting.

### Asset Generation Rule

New visuals are produced as versioned candidate files under `candidates/`,
with prompt, negative prompt, reference, timestamp, resolution, and any exposed
model or seed data recorded in `metadata.md`. Human approval promotes an
unchanged copy to `major/`; candidate history is retained. Images remain static
assets only and introduce no runtime image generation or model dependency.

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

## Approved Major Arcana baseline

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
| VII — The Chariot / 战车 | `major/07_chariot.png` |
| VIII — Strength / 力量 | `major/08_strength.png` |
| IX — The Hermit / 隐士 | `major/09_hermit.png` |
| X — Wheel of Fortune / 命运之轮 | `major/10_wheel_of_fortune.png` |
| XI — Justice / 正义 | `major/11_justice.png` |
| XII — The Hanged Man / 倒吊人 | `major/12_hanged_man.png` |
| XIII — Death / 死神 | `major/13_death.png` |
| XIV — The Temperance / 节制 | `major/14_temperance.png` |
| XV — The Devil / 恶魔 | `major/15_devil.png` |
| XVI — The Tower / 高塔 | `major/16_tower.png` |
| XVII — The Star / 星星 | `major/17_the_star.png` |
| XVIII — The Moon / 月亮 | `major/18_the_moon.png` |
| XIX — The Sun / 太阳 | `major/19_sun.png` |
| XX — Judgement / 审判 | `major/20_judgement.png` |
| XXI — The World / 世界 | `major/21_world.png` |

Candidate history remains in `candidates/`; promotion to `major/` is a copy,
not a move. Do not replace the approved The Star visual master.

## Asset boundary

Visual files remain under `assets/`. Tarot domain JSON and the Native Tool
contract do not embed image bytes and are unchanged by this visual Sprint.
