# Native Agent Rich Experience Integration Design

## Overview

This research freezes a future integration strategy for Starpath rich Tarot
experiences on the installed AstrBot **v4.27.2** source tree. It does not add a
hook, alter a Tool result, change runtime delivery, or send a message.

## Current Architecture

```text
Native Agent -> Starpath Tool -> StarpathRecord
  -> Record Adapter -> Experience Application -> ExperienceResult
  -> Presentation Builder -> PresentationResult -> Presentation Consumer
  -> future runtime-owned platform delivery
```

`starpath.tool.v1` remains business-only. It must not include image paths,
resources, components, or platform payloads.

## AstrBot Lifecycle Analysis

The local v4.27.2 implementation uses `MainAgentHooks` in
`astrbot/core/astr_agent_hooks.py`:

1. `on_tool_start` calls `OnUsingLLMToolEvent`.
2. The tool executor obtains the Tool result.
3. `on_tool_end` clears the current event result and calls
   `OnLLMToolRespondEvent(event, tool, tool_args, tool_result)`.
4. The Agent tool loop continues and produces its final response.
5. Result decoration executes pre-send hooks, then the respond stage delivers
   the chain or stream through the platform adapter.

Thus `on_llm_tool_respond` is the confirmed post-tool, pre-final-Agent hook.
It receives the tool identity, arguments, and returned `CallToolResult`.

## Tool Boundary

The Tool continues to return `starpath.tool.v1` JSON only. It neither invokes
the Experience Application nor accesses an event state. This keeps the Tool
reusable, preserves Native Agent authority, and avoids Tool-to-platform paths.

## Experience Integration Point

The recommended future hook is `on_llm_tool_respond`, filtered to the named
Starpath tool. The integration should validate and parse the existing Tool
result, construct the domain/experience/presentation chain outside the Tool,
and store only the resulting platform-neutral presentation state.

| Candidate | Assessment |
| --- | --- |
| Tool body | Reject: mixes business result with experience/platform concerns. |
| `on_llm_tool_respond` | Recommend: confirmed result is available before Agent final response. |
| `on_decorating_result` | Too late for primary experience construction; use only for final attachment. |
| Independent command | Not appropriate for Agent-selected Tool flow. |

## Presentation Integration Point

The future result hook stores a `PresentationResult` (or an opaque,
request-scoped wrapper) using `event.set_extra`. A final decorating hook reads
it with `event.get_extra`, passes it to the Presentation Consumer, and may
append runtime-prepared image components to the already Agent-authored result.
It must not replace the Agent's text or create new final prose.

## Image Delivery Strategy

For every `ResourceElement`, the future platform-specific integration should
reuse the existing `DisplayResource -> AstrBotImagePayload ->
RuntimeImageDelivery.prepare -> native Image` chain. Presentation and Tool
layers never read image data. Images should be appended to the final result
chain exactly once, after the Agent's final text is available.

## State Passing Strategy

`AstrMessageEvent.set_extra/get_extra` are confirmed local event methods backed
by the event's `_extras` dictionary. They are suitable for request-scoped,
in-memory handoff between the tool-result and decorating phases. Use a
namespaced key, immutable value, and explicit consumed marker; do not store
user profiles, histories, credentials, or durable state.

## Streaming Considerations

The local result-decorate stage calls `on_decorating_result`, but warns that
pre-send hooks may not work correctly when streaming is enabled. It also exits
early for streaming results and tracks `_streaming_finished` to prevent repeat
delivery. Therefore the first implementation should support rich image
attachment only for non-streaming final results. With streaming enabled, it
must retain Agent text delivery and intentionally omit images rather than send
a second message or mutate an active stream.

## Duplicate Send Prevention

Only the normal AstrBot respond stage may deliver. No hook sends directly.
Maintain one request-scoped state object with `consumed=False`; the decorating
hook marks it consumed before attaching elements. If state is absent, consumed,
streaming, or has no valid resource, it makes no attachment. This prevents
both Tool-hook delivery and duplicate final-result attachment.

## Failure Handling

If parsing, experience building, resource conversion, or preparation fails,
record an internal diagnostic and leave the final Agent result unchanged. The
symbolic Tool result remains valid, so the Agent can produce its normal
text-only response. Do not substitute another card or invent content.

## Recommended Implementation Plan

1. Add a separate, feature-gated integration module with mock-only tests.
2. Implement a filtered post-tool hook that stores platform-neutral state.
3. Implement a non-streaming decorating hook that consumes state once.
4. Reuse existing Adapter and Runtime Delivery boundaries for valid resources.
5. Test duplicate prevention, text-only degradation, streaming omission, and
   real QQ delivery only under separate explicit authorization.
