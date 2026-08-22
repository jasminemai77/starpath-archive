# Starpath Multi-Card Tool Contract Evolution

## Status and scope

This document freezes the proposed **`starpath.tool.v2`** result schema.  It is
a design and validation baseline only: the production Native Tool continues to
emit **`starpath.tool.v1`**, and no runtime, Agent authority, QQ, or delivery
behavior changes in this Sprint.

The proposal follows the existing product boundary:

```text
Native Agent -> Tool JSON -> domain/experience consumers
```

It deliberately contains no deck resource, platform payload, sender,
user-profile, or prediction fields.

## Current v1 analysis

`starpath.tool.v1` has a stable top-level object with `record_id`,
`generated_at`, `mode`, `spread`, `star`, a **single flattened** `tarot` draw,
`quote`, and `metadata`.  Its single Tarot object has both card identity/data
and draw data (`orientation`, `draw_keywords`, and `meaning`).

That shape is an excellent single-card contract, but it cannot express a
spread without changing the meaning of `tarot` or adding a second competing
card source.

## Compatibility decision: explicit v2

The selected strategy is **a new contract version: `starpath.tool.v2`**.

Adding an optional `tarot.cards` to v1 was rejected because a single response
could then contain both `tarot.id` and `tarot.cards[*].id`.  Consumers would
need precedence rules, while deployed v1 parsers expect `tarot` itself to be a
card.  This is a structural—not additive—change.

v1 remains the production default and is not migrated by this Sprint.  A
future producer must explicitly set `metadata.contract_version` to
`starpath.tool.v2`; consumers select their parser by that value.  Existing v1
consumers remain unchanged.  A v2 `single` response retains the complete
legacy card/draw semantics inside its sole `cards[0]` entry.

## Proposed v2 JSON schema

```json
{
  "record_id": "starpath-20260822-example",
  "generated_at": "2026-08-22T00:00:00Z",
  "mode": "daily",
  "star": {
    "id": "sirius",
    "name": "Sirius",
    "zh_name": "天狼星",
    "type": "star",
    "astronomy": "Factual astronomy text.",
    "symbolism": "Cultural-symbolic text."
  },
  "tarot": {
    "spread": "three_card",
    "cards": [
      {
        "id": "major-00",
        "name": "The Fool",
        "zh_name": "愚者",
        "number": 0,
        "arcana": "major",
        "suit": null,
        "keywords": ["beginnings"],
        "upright_meaning": ["openness"],
        "reversed_meaning": ["hesitation"],
        "symbolism": {"motif": "threshold"},
        "literary_material": [],
        "image": null,
        "orientation": "upright",
        "draw_keywords": ["openness"],
        "meaning": ["symbolic interpretation"],
        "position": "past",
        "order": 0
      }
    ]
  },
  "quote": {
    "id": "q1",
    "text": "A cultural quotation.",
    "theme": "reflection"
  },
  "metadata": {
    "contract_version": "starpath.tool.v2",
    "content_scope": "symbolic_entertainment"
  }
}
```

### Required fields

The outer fields `record_id`, `generated_at`, `mode`, `star`, `tarot`, `quote`,
and `metadata` remain required.  `star` and `quote` preserve their v1 required
field sets.  `metadata.contract_version` must be exactly `starpath.tool.v2`.

`tarot` is the only structural change:

- `spread` is a non-empty spread identifier (`single`, `three_card`, or a
  later registered value).
- `cards` is a non-empty array of complete Tarot draw objects.
- Each card preserves the v1 fields and adds non-empty `position` plus a
  unique, non-negative integer `order`.
- v2.0 recognizes `main`, `past`, `present`, and `future` positions.  New
  position vocabulary requires a later v2-compatible schema revision and
  accompanying domain support; it is not silently invented at runtime.
- Consumers use `order` as canonical order.  Producers should serialize the
  array in ascending order; the design-time validator canonicalizes it too.

For `single`, use exactly one card with `position: "main"` and `order: 0`.
For `three_card`, use `past`/`present`/`future` at orders 0/1/2.  The proposed
schema intentionally leaves later multi-spread cardinality rules to their
named spread definitions.

## Extensibility and safety

Parsers strictly validate required fields, cardinality, order uniqueness, and
the current position vocabulary.  They accept unknown fields at every level so
additive fields do not break compatible consumers.  Unknown fields must not
alter the semantics of required fields.

Deck selection, visual `asset_key`, and resource paths remain outside this
Tool contract.  The existing deck/asset resolver boundary continues to choose
visuals after a logical card identity is available.

The schema remains entertainment and cultural-symbolism oriented.  It does
not add forecasts, personal profiling, platform delivery, or Agent-generated
final reply content.

## Migration plan

1. Keep `generate_starpath_record` and `starpath.tool.v1` unchanged.
2. Implement a future v2 producer behind an explicit versioned capability or
   distinct tool entry only after a separate implementation Sprint approves it.
3. Dispatch consumers by `metadata.contract_version`; preserve the current v1
   parser for all existing results.
4. Add a v2-to-multi-card domain adapter only when the Experience orchestrator
   gains approved multi-card resolution.
5. Deprecate v1 only through a documented, separately approved release cycle.

No migration, producer, resolver, Runtime, or delivery implementation is
included here.

## Validation baseline

`contracts/starpath_tool_v2.py` is a platform-neutral design-time validator.
Its tests cover a v2 single card retaining all v1 draw semantics, ordered
three-card data, missing required fields, invalid positions, and ignored
additive fields.  It has no AstrBot, OneBot, QQ, or Runtime dependency.
