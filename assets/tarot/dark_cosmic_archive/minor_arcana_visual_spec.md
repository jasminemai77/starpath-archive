# Dark Cosmic Archive — Minor Arcana Visual Specification

## 1. Status and scope

This document defines the production visual language for the 56 Minor Arcana
cards in the `dark_cosmic_archive` visual deck. It is a design specification
only: it does not create assets, change Tarot domain data, add runtime image
dependencies, or alter the Tool Contract.

Minor Arcana is **not a reduced-scale copy of Major Arcana**.

- **Major Arcana**: consequential chapters in the cosmic archive. Each card
  carries a singular, high-density narrative scene.
- **Minor Arcana**: the archive's daily record pages. Each card records an
  elemental state, pattern, relation, or completed system with a repeatable
  visual grammar.

The intended relationship is an historical compendium and its daily log pages,
not 22 protagonist cards followed by 56 lesser protagonist cards. Minor cards
therefore use approximately 70% of Major Arcana's narrative and decorative
density while retaining the same production quality, archival atmosphere, and
card identity.

## 2. Deck continuity

Minor Arcana inherits the frozen Dark Cosmic Archive v1.0 baseline:

- **World**: dark cosmic archive; ancient tarot; celestial atmosphere.
- **Card format**: portrait PNG, 1024 × 1536 px, 2:3 ratio.
- **Base palette**: deep-space blue, nebula purple, restrained antique gold,
  and ivory typography.
- **Border**: fine antique-gold double border with restrained star-chart,
  orbit, and archival marks. Minor borders use 25–30% less corner decoration
  than Major cards.
- **Lighting**: one calm, readable focal light; soft gold highlights; no
  neon, horror-black, game-card UI, or overloaded particle fields.
- **Typography**: clear ivory text, fixed title zones, fixed title tracking,
  and fixed lower whitespace. Long English titles must remain centered and
  legible rather than being compressed into decorative text.

The title treatment remains part of the card system, not an illustration
caption. The upper marker zone carries the rank (`ACE`, `II`–`X`, or
`PAGE`/`KNIGHT`/`QUEEN`/`KING`); the lower zone carries the English card name
and its Chinese name from the approved Tarot data.

## 3. Visual grammar for the four suits

Suit identity is a repeatable visual grammar, not a literal element prop.
Every suit must preserve the common deck border, typography, archival texture,
and compositional restraint while using its own recurring structures.

### Wands — stellar energy cycle

Wands represent a stellar energy cycle: creation, ignition, movement, and
renewal. They are not ordinary flames or fantasy staffs.

- **Primary motifs**: star-flame, solar particles, stellar trajectories,
  radiant filaments, and a restrained archival wand/vector mark.
- **Composition**: a luminous energy source initiates or links orbiting forms;
  trajectories should communicate directed movement.
- **Accent behavior**: antique gold and warm stellar amber appear as focused
  highlights against the common blue-violet field.
- **Avoid**: campfires, generic fireballs, weapon poses, or bright game-fantasy
  effects.

### Cups — emotional star sea

Cups represent an emotional star sea: perception, reflection, resonance, and
flow. They are not rows of ordinary drinking vessels.

- **Primary motifs**: liquid nebulae, galactic water surfaces, moonlit
  reflections, tidal arcs, and a restrained archival cup/basin mark.
- **Composition**: reflections and currents create relationships between forms;
  the focal light may be echoed on a calm cosmic surface.
- **Accent behavior**: moonlit ivory, cool indigo, and softened silver-blue
  remain subordinate to the shared palette.
- **Avoid**: domestic still lifes, realistic beach scenes, or decorative cups
  arranged without a visual state.

### Swords — consciousness and thought structure

Swords represent consciousness and thought structure: observation, clarity,
  tension, orientation, and ordered decision. They are not weapon imagery.

- **Primary motifs**: star-track tangents, optical structures, spatial
  geometry, prismatic planes, precise light edges, and a restrained archival
  blade/axis mark.
- **Composition**: lines, planes, and intersections make an intelligible
  spatial structure, with one decisive focal axis.
- **Accent behavior**: ivory, pale blue, and cold antique-gold edge light are
  controlled and never become cyberpunk neon.
- **Avoid**: combat, attacks, battlefields, gore, or a person simply holding a
  sword.

### Pentacles — cosmic material cycle

Pentacles represent cosmic material cycles: formation, stability, exchange,
  gravity, and enduring structure. They are not coins.

- **Primary motifs**: planetary cores, crystal lattices, mineral strata,
  gravitational orbits, orbital architecture, and a restrained archival
  pentacle/seal mark.
- **Composition**: material forms are assembled, anchored, or circulating in
  gravity; geometry should feel geological or orbital rather than financial.
- **Accent behavior**: mineral violet, deep blue, and antique-gold inclusions
  emphasize mass and age without replacing the deck palette.
- **Avoid**: piles of money, merchant scenes, literal coin collections, or
  ordinary landscape illustration.

## 4. Number-card template system

Number cards (Ace through Ten) are generated from four shared templates, one
per suit. Each template fixes its base environment, central symbol family,
motif placement, lighting logic, and decoration budget. Individual cards vary
the **state of the system**, not merely the count of an object.

The rank is expressed as:

`rank + state change + suit visual grammar`

For example, Five of Cups must show a changed relationship in the emotional
star-sea system; it must not be five disconnected cups placed on a page.

| Rank stage | Ranks | Required visual behavior |
| --- | --- | --- |
| Beginning | Ace | One clear core symbol; the elemental system first appears. |
| Development | 2–4 | Relationships, balance, exchange, or emerging variation between forms. |
| Tension | 5–7 | A visible structural change, interruption, divergence, or reorientation. |
| Maturity | 8–10 | A coherent complete system, accumulation, integration, or settled pattern. |

The number may be legible through the count of primary motifs, but count is
never the full composition. Secondary stars, particles, border marks, and
background noise are not counted as rank motifs. Use negative space to keep
the state readable at card size.

### Per-suit template requirements

| Suit | Base environment | Central symbol family | Motif layout | Lighting and decoration |
| --- | --- | --- | --- | --- |
| Wands | stellar nursery or solar field | star-flame / energy vector | radiating or orbital trajectories | warm core, restrained solar particles |
| Cups | galactic sea or reflective nebula | liquid vessel / luminous tide | reflected arcs and linked ripples | moonlit focal reflection, sparse droplets |
| Swords | spatial observatory or abstract light field | axis / tangent / optical plane | intersecting geometry with a clear direction | cool edge light, precise sparse marks |
| Pentacles | planetary interior or orbital ruin | core / lattice / gravity seal | anchored clusters and orbital rings | mineral glow, subtle gold inclusions |

## 5. Court-card system

Court cards are **personifications of elemental consciousness**, not real
people, role-play avatars, celebrity likenesses, or conventional portraits.
An optional human-like silhouette may serve the composition, but it must be
partial, symbolic, and inseparable from the elemental structure. Faces must
not become the card's primary subject.

Rank progression is consistent across all suits:

| Court rank | Archetypal visual role |
| --- | --- |
| Page | first contact, study, signal, or emerging awareness |
| Knight | directed motion, transmission, pursuit, or activated force |
| Queen | inward attunement, stewardship, integration, or receptive mastery |
| King | outward order, durable structure, articulation, or expressed mastery |

Apply the role through the suit grammar: a King of Swords is Air Element plus
rational order and decision structure, not a person holding a sword; a Queen
of Cups is Water Element plus perception and inner equilibrium, not a female
portrait. Clothing, thrones, crowns, and gendered royal-costume clichés are
not required and should not override the cosmic archive identity.

## 6. Symbolic language boundary

All visual direction and supporting production notes describe **symbolism**,
symbolic meaning, cultural reference, elemental patterns, and composition.
They must not claim prediction or prescribe a viewer's future, destiny,
wealth, relationships, or inevitable events. This is an entertainment visual
system and an archival symbolic language, not a forecasting system.

## 7. Future deck compatibility

Each Minor Arcana card must retain a stable, deck-independent card identifier
and asset key. A visual deck resolves an asset for that stable key; the Tarot
domain record must not embed a deck-specific image path.

Example production identity:

```json
{
  "id": "cups_05",
  "asset_key": "cups_05_five"
}
```

The same key can later be represented by `dark_cosmic_archive`, `nebula_dream`,
`ancient_library`, or `moon_garden` without changing the card's domain
identity. Deck IDs, asset paths, generated-image settings, and candidate
history belong to visual asset metadata, not to Tarot content records.

## 8. Universal generation requirements

Every future production prompt must include:

1. `Dark Cosmic Archive` visual deck identity and the frozen v1.0 baseline.
2. Portrait tarot card, 1024 × 1536 px, 2:3 ratio, with the fixed gold border
   and title zones.
3. The applicable suit grammar, rank stage, template, and focal-light rule.
4. Exact rank marker, English title, and Chinese title supplied from approved
   Tarot data; no additional explanatory copy.
5. Controlled decorative density: quiet cosmic background, readable central
   state, and no more than the Minor Arcana decoration budget.
6. Negative constraints: no generic fantasy UI, cyberpunk neon, realistic
   portrait avatar, weapon combat, literal money imagery, prediction text, or
   unrelated long copy.

Reference use is stylistic only. The approved `The Star` image remains the
master reference for palette, proportion, border craft, typography, and
lighting discipline; it must not be copied as a scene template for Minor
cards.

## 9. Difference from Major Arcana

| Dimension | Major Arcana | Minor Arcana |
| --- | --- | --- |
| Archive role | consequential chapter | daily record page |
| Narrative | singular, high-density scene | elemental state or system |
| Illustration density | 100% baseline | approximately 70% baseline |
| Reuse | card-specific composition | suit template plus rank progression |
| Recognition | archetypal chapter identity | rank, suit grammar, and state change |

## 10. Production sequence

No assets are created by this specification. When visual production is
authorized, follow this staged validation order:

1. **Phase 1 — 12 prototypes**: Ace, Five, and King for Wands, Cups, Swords,
   and Pentacles. Review suit recognition, rank progression, court restraint,
   typography, and Major compatibility.
2. **Phase 2 — 40 number cards**: Ace through Ten for each suit, using the
   approved templates and rank-state rules.
3. **Phase 3 — 16 court cards**: Page, Knight, Queen, and King for each suit,
   using elemental personification rather than portrait conventions.

Any change to the frozen Major baseline or to the Minor grammar after prototype
approval requires an explicit new visual specification version.
