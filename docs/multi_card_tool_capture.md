# Versioned Multi-Card Tool Capture

Sprint 3D-5.3 adds consumption support for future
`starpath.tool.v2` results at the existing post-Tool capture boundary.  It does
not add a v2 producer, modify `starpath.tool.v1`, change Native Agent
authority, or perform platform delivery.

## Dispatch boundary

`StarpathToolContractDispatcher` reads only the captured JSON object's
`metadata.contract_version`.

```text
CallToolResult text
  -> ToolResultExtractor
  -> StarpathToolContractDispatcher
     -> starpath.tool.v1 -> StarpathRecord
     -> starpath.tool.v2 -> V2TarotExperiencePayload
  -> Capture hook
  -> TarotExperienceApplication
  -> PresentationResult in event extra
```

Unknown, missing, and malformed versions fail capture safely.  The hook stores
`capture_status="failed"` and leaves the Agent's ordinary response path
unmodified.

## v1 compatibility

For `starpath.tool.v1`, the dispatcher delegates to the existing
`StarpathToolResultParser` unchanged.  The capture hook uses the same
`TarotExperienceApplication.build(record, deck_id, spread)` call as before;
`spread` still comes from the Tool arguments.  No v1 field, Tool definition,
or producer behavior changed.

## v2 multi-card mapping

For `starpath.tool.v2`, the existing platform-neutral v2 schema parser first
validates the complete payload.  The dispatcher then maps every v2
`tarot.cards[]` item to a `TarotCardSelection`:

- `id` -> `card_id`
- `position` -> semantic position
- `order` -> ordering
- `name` -> `card_name`
- `meaning` -> source-backed display meaning

It constructs a `TarotSpread`, which enforces the supported `single` and
`three_card` shapes.  V2 quote data becomes `FortuneContext`.  The resulting
`V2TarotExperiencePayload` deliberately has no deck ID; the capture hook
injects the selected deck through the existing `DeckProvider`, then calls
`TarotExperienceApplication.build_input`.

This allows the three-card Experience and existing resolver/presentation code
to run without embedding visual-deck or platform data in the Tool contract.

## Scope and deferred work

The only registered Native Tool still produces v1.  A separate approved Sprint
is required before producing v2 JSON or exposing a new Tool capability.

This integration does not add QQ, AstrBot messaging, image sending, Runtime
delivery, or final-reply ownership.  It only captures an already-returned v2
result into the same platform-neutral PresentationResult event extra used by
v1.
