# Dark Cosmic Archive — Minor Arcana Generation Template

## 1. Purpose and boundary

This document freezes the production template for 56 Minor Arcana cards in the
`dark_cosmic_archive` visual deck. It inherits the approved Dark Cosmic Archive
v1.0 baseline and the Minor Arcana visual specification.

- **Major Arcana — Cosmic Archive Chapters**: singular, high-density chapters.
- **Minor Arcana — Daily Cosmic Records**: symbolic, repeatable elemental
  records of states, relationships, and changes.

Minor Arcana is not a smaller version of Major Arcana. It uses about 70% of
Major narrative and decorative density while retaining the same quality,
readability, archive atmosphere, and visual discipline. This is a production
document only: it creates no images, formal assets, runtime behavior, or Tarot
domain changes.

## 2. Prototype rules inherited from Batch 01

| Validated dimension | Frozen production rule |
| --- | --- |
| Deck continuity | Retain deep-space archive field, antique-gold frame, top rank zone, and fixed lower title band. |
| Suit grammar | Wands = energy trajectories; Cups = liquid reflections; Swords = optical geometry; Pentacles = crystal/gravity structures. |
| Rank progression | Ace is a single core; Five is a changed system; King is stable external elemental order. |
| Court restraint | Court cards use non-human elemental personification, never a real-person royal portrait. |
| Typography | English and Chinese titles are clear, centered, high contrast, and contain no explanatory copy. |
| Candidate discipline | Each candidate PNG has metadata; human review is required before formal archiving. |

These prototypes validate the grammar, not a scene to be copied. Each future
card must create a readable rank-specific state within the suit template.

## 3. Fixed deck style

| Item | Rule |
| --- | --- |
| Deck style | `Dark Cosmic Archive v1.0`: ancient cosmic archive, celestial atmosphere, premium restraint. |
| Resolution | 1024 × 1536 px |
| Ratio | 2:3 portrait |
| Color System | Deep Space Blue dominant; muted Nebula Purple depth; Antique Gold structure/highlights; Ivory typography and starlight. |
| Border System | Inherit Major's antique-gold double border, but simplify star-track, orbit, and chart decoration. |
| Lighting Rule | Stable, soft, clear one-source illumination; do not use Major-scale theatrical narrative lighting. |
| Density | Approximately 70% of Major density; protect negative space and one primary symbol. |

Avoid horror-black imagery, neon cyberpunk, anime, generic fantasy posters, and
modern game-card UI.

## 4. Typography and layout template

All text is supplied verbatim from approved Tarot data.

| Zone | Rule |
| --- | --- |
| Top | Centered rank marker: `ACE`, Roman `II`–`X`, or `PAGE` / `KNIGHT` / `QUEEN` / `KING`. Numeric ranks preserve the Roman-number zone. |
| Central field | One symbolic suit-and-rank composition; no keywords, body copy, or descriptive text. |
| English name | Centered uppercase serif name in the upper line of the fixed lower title band. |
| Bottom | Centered, readable Chinese name below English. |

Letter spacing, title-band height, and bottom whitespace are fixed. Long English
titles reduce type size before tracking; they never wrap, stretch, or use a
random/modern font. No text may collide with the border.

## 5. Four-suit production templates

### Wands — stellar energy cycle

| Background | Subject | Lighting | Decoration | Avoid |
| --- | --- | --- | --- | --- |
| Stellar nursery or solar field in muted blue-violet depth | Star-flame, solar particles, radiant filaments, directed stellar trajectories | One warm stellar core, restrained gold highlights | Sparse orbital vectors and archive marks supporting motion | Ordinary flames, torches, weaponized staffs, fireball/game-spell effects |

### Cups — emotional star sea

| Background | Subject | Lighting | Decoration | Avoid |
| --- | --- | --- | --- | --- |
| Galactic water surface or liquid nebula with moonlit depth | Luminous basin/cup mark, tidal arcs, liquid stars, reflections | One cool ivory moonlit reflection, softened gold edges | Sparse ripples/orbits; reflections must reveal relationships | Domestic still life, ordinary beach scene, unrelated cups, realistic portrait |

### Swords — consciousness structure

| Background | Subject | Lighting | Decoration | Avoid |
| --- | --- | --- | --- | --- |
| Abstract cosmic observatory or spatial light field | Geometric light axis, star-track tangent, optical plane, abstract light blade | Clear ivory/pale-blue focal intersection, cold antique-gold edge light | Sparse chart geometry clarifying direction and structure | War, battle, weapon display, soldiers, gore, cyberpunk UI |

### Pentacles — cosmic material cycle

| Background | Subject | Lighting | Decoration | Avoid |
| --- | --- | --- | --- | --- |
| Planetary interior, mineral cloud, orbital ruin, or gravity field | Planetary crystal, stellar mineral, gravity seal, lattice, orbital architecture | One mineral-violet or antique-gold internal glow | Restrained gravity rings, crystal inclusions, archival orbit marks | Coins, money, merchants, wealth symbols, financial UI |

## 6. Number-card rules — 40 cards

Numeric rank is never a literal count of disconnected objects. Each card is:

`rank + state change + suit visual language`

| Rank stage | Ranks | Required behavior |
| --- | --- | --- |
| Beginning | Ace | One clear core symbol; minimum complexity and initial elemental emergence. |
| Development | 2–4 | Relationships, exchange, balance, interaction, or emerging variation. |
| Tension | 5–7 | Reorientation, interruption, divergence, or controlled structural conflict. |
| Maturity | 8–10 | Coherent complete system, integration, accumulation, or settled cycle. |

Primary motifs may make the count legible, but stars, frame ornaments, and
incidental particles never count. Use negative space so the state reads at
thumbnail scale.

## 7. Court-card rules — 16 cards

Court cards are elemental consciousness personified through suit grammar, not
real people, role-play avatars, celebrity likenesses, or conventional
portraits. A partial symbolic silhouette is allowed only if it remains
subordinate to the elemental structure.

| Court rank | Archetypal action |
| --- | --- |
| Page | Exploration, study, first signal, emerging awareness. |
| Knight | Directed action, motion, transmission, activated change. |
| Queen | Inner attunement, stewardship, integration, receptive mastery. |
| King | External order, durable structure, articulation, expressed mastery. |

Apply rank action through the suit template. King of Swords is ordered
air/geometry, not a person holding a sword; King of Pentacles is stabilised
gravity/material architecture, not a finance portrait. Crowns, thrones, armor,
and gendered royal costumes are not required.

## 8. Universal image-generation prompt template

Replace bracketed values from the approved Tarot card and relevant suit table.

```text
Create one finished vertical tarot card for Starpath Archive.

Card identity: [CARD_ID], [RANK], [ENGLISH_CARD_NAME], [CHINESE_CARD_NAME].
Deck style: Dark Cosmic Archive v1.0; ancient cosmic archive, celestial
atmosphere, premium painterly tarot illustration; Minor Arcana daily cosmic
record, approximately 70% of Major Arcana narrative density.
Format: 1024 × 1536 px, 2:3 portrait; restrained aged antique-gold double
border; sparse star-chart/orbit accents; clear top rank zone; fixed lower title
band; one calm readable focal subject and protected negative space.
Color: deep-space blue, muted nebula purple, antique gold, ivory typography.
Suit visual language: [SUIT_BACKGROUND]; [SUIT_SUBJECT]; [SUIT_LIGHTING];
[SUIT_DECORATION]. Rank state: [RANK_STATE_CHANGE].
Text (verbatim): top "[RANK_MARKER]"; English "[ENGLISH_CARD_NAME]";
Chinese "[CHINESE_CARD_NAME]". Render these strings correctly, centered,
clear, high contrast, with no other text.
```

### Required negative prompt

```text
modern UI, game card style, cartoon, anime, realistic portrait, role-play
avatar, excessive fantasy armor, horror, warfare, religious copy, fortune
telling claims, prediction wording, extra copy, garbled text, misspelled text,
watermark, neon cyberpunk, crowded border, and [SUIT-SPECIFIC AVOIDS]
```

Use `The Star` only for palette, proportion, border craft, typography, and
calm-lighting discipline—not as a scene to copy.

## 9. Candidate metadata template

Each candidate is stored beside a `metadata.md`:

```text
# Card Metadata

Card ID: `[CARD_ID]`
Asset Key: `[ASSET_KEY]`
Deck: `dark_cosmic_archive`
Version: `1.0`
Generation Prompt: [final prompt]
Negative Prompt: [final negative prompt]
Resolution: `1024 × 1536` (2:3)
Generation Date: `[YYYY-MM-DD]`
Reference: [visual-spec and reference assets]
Status: `candidate`
```

Record model, seed, and settings when exposed; otherwise explicitly state that
they were unavailable. Retain candidate history even for rejected outputs.

## 10. Formal production sequence — 56 cards

Produce by suit. Do not promote automatically and do not start the next suit
until the current suit receives human review.

| Batch | Scope | Gate |
| --- | --- | --- |
| Batch 1 | Wands — 14 cards | Generate candidates → human review → formal archive → proceed. |
| Batch 2 | Cups — 14 cards | Generate candidates → human review → formal archive → proceed. |
| Batch 3 | Swords — 14 cards | Generate candidates → human review → formal archive → proceed. |
| Batch 4 | Pentacles — 14 cards | Generate candidates → human review → formal archive → complete set. |

Inspect exact title text, resolution, ratio, border, deck palette, suit grammar,
rank-state readability, density, prohibited imagery, and metadata completeness.

Future formal layout, created only after approval:

```text
assets/tarot/dark_cosmic_archive/minor/
  wands/
  cups/
  swords/
  pentacles/
```

This Sprint does **not** create `minor/` or copy candidates into it.

## 11. Stable identity and future deck compatibility

Use deck-independent fields in visual metadata:

```json
{
  "card_id": "cups_05",
  "asset_key": "cups_05_five"
}
```

Do not use `dark_cosmic_archive_cups_05` as a card identity. Future decks such
as `nebula_dream`, `ancient_library`, or `moon_garden` must resolve the same
card identity without changing the Tarot domain record. Deck paths remain
visual metadata, never embedded image paths in Tarot content.

## 12. Production checklist

- [ ] Card ID and deck-independent asset key are correct.
- [ ] Prompt uses the correct suit template and rank-state rule.
- [ ] Resolution is 1024 × 1536; ratio is 2:3.
- [ ] Top rank, English title, and Chinese title are exact and readable.
- [ ] Color, border, spacing, and lighting inherit Dark Cosmic Archive v1.0.
- [ ] Minor density is controlled; no Major-scale scene is produced.
- [ ] No UI, game-card, portrait, warfare, finance-symbol, or predictive claim appears.
- [ ] Candidate PNG and complete metadata exist.
- [ ] Human review occurs before archiving or the next batch.
