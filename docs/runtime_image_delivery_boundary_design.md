# Runtime Image Delivery Boundary Design

## Overview

The visual chain now produces an `AstrBotImagePayload`, but that payload still
contains only a package-relative resource reference. Runtime Image Delivery is
the minimum boundary that safely prepares that reference for a future AstrBot
Runtime sender.

This Sprint implements a prepare-only contract. It validates a local path and
returns metadata; it does not read image bytes, build an AstrBot native message
component, upload media, call an AstrBot API, or send anything.

## Current Architecture

```text
card_id
  -> DefaultAssetResolver
  -> AssetReference
  -> AssetReference Consumer
  -> DisplayResource
  -> AstrBotAdapter
  -> AstrBotImagePayload
  -> RuntimeImageDelivery.prepare()
  -> PreparedAstrBotResource
  -> future AstrBot Runtime sender
  -> future event send
```

The current Native Tool entry point remains asynchronous but only produces its
existing structured business result. It does not call this delivery boundary.

## Responsibility Boundary

| Layer | Responsibility | Explicitly not responsible for |
| --- | --- | --- |
| Tarot Domain | Logical card identity and symbolic data. | Images or resource paths. |
| Resolver / Manifest Provider | Map `deck_id + card_id` to `AssetReference`. | Filesystem access or sending. |
| Asset Consumer | Convert `AssetReference` to `DisplayResource`. | Resource lookup or platform delivery. |
| AstrBot Adapter | Convert `DisplayResource` to `AstrBotImagePayload`. | File access, native message objects, sending. |
| Runtime Image Delivery | Safely prepare one local resource reference. | Card lookup, image decoding, message construction, sending. |
| Future AstrBot Runtime Sender | Build native message components and invoke platform send. | Domain or resolver work. |

Future Experience Orchestration is responsible for calling the AstrBot Adapter
after it already has a `DisplayResource`. `RuntimeImageDelivery` does not call
the adapter; it receives the completed `AstrBotImagePayload`.

## Delivery Interface

The contract is located in `experience/delivery/`, separate from the existing
`adapter/` AstrBot Native Tool boundary. The directory owns the generic runtime
preparation step while `adapter/astrbot_platform.py` remains responsible for
AstrBot payload conversion. This avoids changing the tool entry point or
mixing preparation with message delivery.

```python
class RuntimeImageDelivery(ABC):
    def prepare(self, payload: AstrBotImagePayload) -> PreparedAstrBotResource:
        ...
```

`prepare`, rather than `send`, is intentional: preparation creates no platform
side effect. `LocalRuntimeImageDelivery` is the smallest concrete contract for
the current one-local-root, PNG-only situation. A separate `ResourceLocator`
abstraction is not warranted yet because there is only one local deck root and
no repeated multi-platform storage use.

## Resource Path Resolution

`AstrBotImagePayload.resource` remains a relative reference such as
`minor/cups/cups_05_five.png`. `LocalRuntimeImageDelivery`, with an injected
deck asset root, is the only layer in this chain that converts it to a local
path.

The delivery boundary supplements earlier metadata validation with the checks
required before local runtime access:

1. Reject empty references, absolute POSIX paths, absolute Windows paths,
   backslash paths, directory traversal, and non-PNG suffixes.
2. Resolve the candidate from the injected asset root.
3. Confirm the resolved target remains inside that root.
4. Confirm the root is a directory, the target exists, and it is a regular
   file.
5. Return only the resolved path metadata; do not open or mutate the file.

## Prepared Resource Model

```python
PreparedAstrBotResource(
    resource_type="image",
    resolved_path=".../major/17_the_star.png",
    media_type="image/png",
    metadata={"deck_id": "dark_cosmic_archive", "card_id": "major-17"},
)
```

The model contains no event, bot, group, user, send callable, or user state.
It is a safe handoff to a future sender, not a native AstrBot message object.

## AstrBot Runtime Boundary

```text
AstrBotImagePayload
  -> RuntimeImageDelivery.prepare()
  -> PreparedAstrBotResource
  -> future AstrBot Runtime Sender
  -> native message component
  -> future platform send
```

Runtime Delivery prepares a verified local location. A separately authorized
AstrBot Runtime Sender owns native message-component construction, any image
upload or encoding, and the final asynchronous send. No common delivery class
imports a QQ- or OneBot-specific component.

## Error Handling

| Error | Condition |
| --- | --- |
| `RuntimePayloadPreparationError` | Payload is absent or structurally unsuitable for preparation. |
| `InvalidRuntimeResourceError` | Reference is unsafe, outside the root, non-PNG, or does not resolve to a regular file. |
| `RuntimeResourceNotFoundError` | Reference is valid but the runtime file is missing. |
| `RuntimeResourceAccessError` | Configured root or resource cannot be safely inspected. |

All errors inherit `RuntimeDeliveryError`. Resolver and Manifest Provider
continue to report their own errors and never absorb runtime failures.

## Failure / Degradation Strategy

Visual delivery is an experience enhancement, not the Tarot business result.
If preparation fails after a record has been generated, a future orchestration
or runtime sender may choose a text-only result and report the delivery error
observably. That policy belongs above this boundary; no automatic fallback,
error swallowing, or message generation is implemented in this Sprint.

## Async Boundary

`prepare()` is synchronous because it performs only small local metadata and
file-status checks. Resolver, Consumer, Adapter, and Delivery preparation stay
synchronous. The future AstrBot Runtime Sender is the first asynchronous
boundary because platform I/O, upload, and sending are naturally async; no
upstream interface should be made async prematurely.

## Security Considerations

- Asset roots are injected, not inferred from user input.
- References may not be absolute or traverse outside the root.
- The resolved target must remain within the configured root and be a regular
  PNG file.
- Delivery never reads image content, changes assets, uses network access, or
  receives user identifiers.
- There is no event, bot, direct-message, group, scheduling, or proactive
  sending capability in this package.

## Compatibility Notes

This boundary does not change:

- Tarot Domain or logical card identity.
- Tool Contract and existing structured tool results.
- Resolver or Manifest Provider interfaces.
- Existing `StarpathExperience` organization behaviour.
- Current AstrBot Native Tool entry point, Runtime, Agent permissions, or
  event flow.
- Visual metadata, candidate history, or PNG assets.

## Next Sprint

A separate, explicitly authorized Sprint may define an AstrBot Runtime Sender
interface that receives `PreparedAstrBotResource`, constructs the appropriate
native message component, and provides mock-based—not real-platform—delivery
tests. Actual platform sending requires separate runtime and user-flow review.
