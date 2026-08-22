# Tarot Experience Flow Design

## Overview

This document freezes the design boundary for a future Tarot experience flow.
It connects the existing symbolic record tool with the visual asset pipeline
without making either layer responsible for final chat prose or transport.

Starpath Archive remains an entertainment and cultural-symbolism system. Its
flows must not present predictions, guarantees, personal profiles, or destiny
judgements.

## Current Architecture

The current Native Tool produces the stable `starpath.tool.v1` JSON contract:

```text
Native Agent
  -> generate_starpath_record
  -> StarpathToolAdapter
  -> StarpathService / Tarot Domain
  -> StarpathExperience
  -> structured business result
```

The separate visual pipeline is already available:

```text
deck_id + card_id
  -> DeckManifestProvider
  -> DefaultAssetResolver
  -> AssetReference
  -> AssetReferenceConsumer
  -> DisplayResource
  -> AstrBotAdapter
  -> AstrBotImagePayload
  -> RuntimeImageDelivery.prepare
  -> PreparedAstrBotResource
  -> AstrBot native Image component (runtime-owned)
```

`StarpathToolAdapter` does not invoke this visual pipeline. This remains the
correct current boundary.

## User Flow

The Native Agent interprets a request and selects an explicitly available
Starpath capability. The tool returns only structured symbolic business data.
A future Experience Orchestrator may turn the selected logical card identities
into display resources. The Native Agent, not the plugin, owns final natural
language; the AstrBot runtime owns final message delivery.

```text
User request -> Native Agent -> Tool result -> Experience plan
    -> optional image preparation -> Agent response plan -> AstrBot runtime
```

## Quick Mode

Example intent: “帮我看看今天运势”. The user-facing wording remains the
Native Agent's responsibility and should be framed as symbolic entertainment.

1. The Agent calls the existing `generate_starpath_record(mode="daily",
   spread="single")` tool.
2. The Tool returns one `tarot.card.id`, one star record, one quote, and
   metadata. It returns no image location or AstrBot object.
3. `TarotExperienceOrchestrator` (future) reads the logical card id and a
   selected `deck_id`, then produces at most one `DisplayResource`.
4. The Agent may form a concise response from three text sections: celestial
   context, card symbolism, and quote/lucky-sign context. The optional card
   image accompanies it when preparation succeeds.

Quick mode therefore has one card, zero or one optional image, and no
plugin-generated final chat text.

## Full Mode

Example intent: “做一次完整占卜”. Full mode is a designed composition, not a
newly implemented spread in this Sprint.

```text
celestial context
  + tarot spread result (one or more positioned cards)
  + symbolic fortune sign / quote
  -> ExperienceResult
  -> optional ordered card images
```

The first supported implementation may still use a single card while exposing
an ordered list shape. When a future domain spread is introduced, the
orchestrator can preserve card order and positions such as `past`, `present`,
and `future` without changing image resolution mechanics. A Celtic Cross and
relationship spreads are future domain capabilities, not this Sprint's work.

Full mode has one star section, one Tarot section containing an ordered card
list, one symbolic quote/sign section, and zero to the number of selected
cards optional images. The Agent chooses how much language to present.

## Fortune Sign

The existing quote is a cultural and symbolic “lucky sign” element. It is not
a forecast, instruction, or claim about a user's future. It remains Tool
business data (`quote.id`, `quote.text`, `quote.theme`); Experience may order
it as a text section but must not reinterpret it into certainty language.

## Tool Contract

`starpath.tool.v1` remains unchanged in this Sprint:

```json
{
  "record_id": "...",
  "generated_at": "...",
  "mode": "daily",
  "spread": "single",
  "star": {},
  "tarot": {"id": "major-00"},
  "quote": {},
  "metadata": {"contract_version": "starpath.tool.v1"}
}
```

It deliberately contains neither `image_path`, `image_url`, `asset_key`, an
AstrBot payload, nor an AstrBot component. Logical identities such as
`card_id` are sufficient for a later visual lookup.

A future domain-facing result may be normalised internally as:

```python
TarotReadingResult(
    spread="three_card",
    cards=(
        CardSelection(card_id="major-00", position="past"),
        CardSelection(card_id="cups_05_five", position="present"),
        CardSelection(card_id="major-17", position="future"),
    ),
    symbolic_context={},
    metadata={},
)
```

This is a design model only. It does not alter the current Tool Contract or
implement a three-card domain spread.

## Experience Orchestrator

The future `TarotExperienceOrchestrator` accepts a business result plus an
explicit `deck_id`. It returns an `ExperienceResult` containing:

- ordered logical card selections;
- ordered `DisplayResource` values when visual resolution succeeds;
- platform-neutral text-section data;
- non-user-facing delivery diagnostics when a visual enhancement fails.

It may call the resolver once per `card_id`, then use the existing consumer.
It does not generate final prose, access chat history, create user profiles,
call an LLM, build AstrBot native components, or send a message.

## Image Integration

Images originate only after the Tool phase:

```text
Tool card_id
  -> Experience resolves deck_id + card_id
  -> DisplayResource
  -> AstrBot adapter payload
  -> Runtime prepares local file
  -> runtime constructs native image component and sends it
```

The visual chain is an enhancement. If resolution, preparation, or component
construction fails after the business result succeeds, the Experience result
remains valid with its text sections and no corresponding display resource.
The Agent may issue a text-only response. Failures are observable to runtime
logs/diagnostics but are not silently converted into invented content.

## Agent Boundary

The Native Agent exclusively interprets user intent, selects a tool, and forms
the final language response. The plugin must not reply to users directly,
modify Agent personality, read chat history, create Agents, or build user
profiles. It returns structured symbolic content only.

## AstrBot Boundary

The AstrBot Adapter converts a `DisplayResource` into
`AstrBotImagePayload`; `RuntimeImageDelivery` validates and resolves the local
PNG. A runtime-owned integration can then construct `Comp.Image.fromFileSystem`
and yield an event result. The previous live smoke test verified that path;
its temporary command was removed and is not a user feature.

Neither the Tool nor the Experience Orchestrator calls `event.send`, OneBot,
NapCat, base64 encoding, or platform-specific send APIs.

## Error Handling

| Condition | Experience policy |
| --- | --- |
| Invalid Tool input | Preserve the Tool's structured parameter error. |
| Unknown deck or card | Keep symbolic result; omit that image and record a diagnostic. |
| Missing or unsafe local resource | Keep symbolic result; omit that image and record a diagnostic. |
| Platform component/delivery failure | Runtime reports it; Tool result and Agent text plan remain valid. |

No fallback may substitute a different logical card or create a path in the
Tool result.

## Future Spread Extension

New spreads add ordered `CardSelection` values with stable `card_id` and
semantic `position`; they do not add resource paths. The same orchestrator
loop resolves one display resource per selected card, allowing `single`,
three-card, Celtic Cross, and relationship layouts to share the same boundary.

## Multi Deck Compatibility

`deck_id` is an Experience-level selection supplied to the resolver. No
Experience model may hard-code `dark_cosmic_archive`. This permits another
visual deck to map the same logical `card_id` to a different asset while the
Tarot Domain and Tool Contract remain unchanged.

## Compatibility Notes

This is a design and contract-test Sprint. It does not modify Tarot Domain,
the Native Tool Contract, Agent permissions, AstrBot Runtime, deck assets, or
manifest data.
