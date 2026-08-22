# Multi-Card Spread Domain Design

## Scope

This design extends the platform-neutral Tarot experience domain vocabulary. It
does not change the Tool JSON, asset resolver, message presentation, QQ adapter,
runtime, or AstrBot hooks.

## Domain Models

- `SpreadType` currently defines `SINGLE` (`single`) and `THREE_CARD`
  (`three_card`). Further shapes may be introduced by adding an enum value and
  its declared position shape; Celtic Cross is intentionally not defined.
- `CardPosition` defines `MAIN`, `PAST`, `PRESENT`, and `FUTURE`.
- `TarotCardSelection` now carries `card_id`, a validated `position`, and a
  non-negative `order`. Its default `order=0` preserves existing single-card
  callers.
- `TarotSpread` validates a complete ordered spread: single requires `MAIN`;
  three-card requires `PAST`, `PRESENT`, then `FUTURE` after sorting selections
  by `order`.

## Backward Compatibility

`TarotExperienceInput` remains unchanged at its public shape: `deck_id`,
`spread`, `cards`, and optional `fortune_context`. Existing callers may keep
passing `spread="single"` and `TarotCardSelection(card_id, "main")`.
String positions are normalised to the new enum, while generated single-card
text continues to use its stable `main: <card_id>` form.

Unknown future spread strings remain valid input values so later orchestration
support can be added without changing the input contract. `TarotSpread` itself
only validates declared shapes.

## Future Orchestrator Entry

The current `TarotExperienceOrchestrator` remains deliberately single-card:
it continues to resolve exactly one `TarotExperienceInput` card for
`spread="single"`. A later implementation can accept a validated
`TarotSpread`, resolve its ordered `cards`, and create multiple display
resources and text sections. That work is explicitly outside this Sprint.
