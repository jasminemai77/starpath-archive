# Platform Adapter Interface Design

## Overview

`PlatformAdapter` is the final isolation boundary before a future platform
sender. It receives a platform-neutral `DisplayResource` and produces a
platform-neutral `PlatformPayload`. The payload is a conversion description,
not a message and not a request to transmit a resource.

This Sprint defines the interface, model, errors, and deterministic metadata
conversion only. It does not implement any specific platform, message protocol,
or sending behaviour.

## Architecture Boundary

The resource chain separates concerns at every stage:

```text
Resolver: card_id + deck_id -> AssetReference
Consumer: AssetReference -> DisplayResource
Adapter: DisplayResource -> PlatformPayload
Sender: PlatformPayload -> future platform transport
```

The Resolver finds a visual resource. The Consumer creates presentation-ready
metadata. The Adapter describes the payload shape expected by a later
platform-specific sender. No core component knows a specific platform or
message wire format.

The adapter does not look up cards, read manifests, open files, determine user
permissions, or perform business logic.

## Interface Design

```python
class PlatformAdapter(ABC):
    def adapt(self, resource: DisplayResource) -> PlatformPayload:
        ...
```

The interface accepts an already-created `DisplayResource`, so it has no
dependency on a resolver, manifest provider, JSON storage, or deck identity.
The abstract method reserves platform policy for future implementations. The
`PlatformPayload.from_display_resource()` factory establishes the generic,
deterministic conversion contract without selecting or invoking a sender.

## PlatformPayload Model

```python
PlatformPayload(
    payload_type="image",
    content="major/17_the_star.png",
    metadata={
        "format": "png",
        "deck_id": "dark_cosmic_archive",
        "card_id": "major-17",
    },
)
```

| Field | Meaning |
| --- | --- |
| `payload_type` | Generic payload category; the current visual contract produces `image`. |
| `content` | Resource reference carried from the display path; it is not image bytes or message text. |
| `metadata` | Generic context, including source format and display metadata. |

The model intentionally has no platform name, CQ code, OneBot object, channel,
recipient, user ID, or delivery status.

## Conversion Flow

1. The Consumer supplies a validated `DisplayResource`.
2. The Adapter verifies the resource type and the generic required fields.
3. The Adapter produces a `PlatformPayload` with image type, relative resource
   reference, and copied metadata.
4. A separately scoped future sender decides whether and how to transmit it.

The generic adapter never reads the path or checks whether an image exists; it
performs no filesystem or transport I/O.

## Error Handling

| Condition | Error |
| --- | --- |
| Missing or incomplete display metadata | `InvalidDisplayResourceError` |
| Unsupported generic resource type, such as `video` | `UnsupportedResourceTypeError` |
| A future platform-specific conversion fails | `AdapterConversionError` or a platform-specific subclass |

All errors are explicit. No conversion silently omits content, constructs a
fallback message, or sends data.

## Multi Platform Extension

```text
DisplayResource
  -> PlatformAdapter
     -> future AstrBot adapter
     -> future Web adapter
     -> future Discord adapter
     -> future Telegram adapter
     -> future CLI adapter
```

Each future implementation can convert `PlatformPayload` into its own local
transport type without modifying the Resolver, Consumer, Tarot Domain, or
Manifest Provider. A platform implementation remains responsible for its own
permissions, delivery errors, and protocol details.

## Compatibility Notes

This contract does not change:

- Tarot Domain or logical card identity.
- Tool Contract, message structure, or Agent permissions.
- Runtime and AstrBot/QQ integration.
- Resolver and Manifest Provider interfaces or implementations.
- Existing visual metadata or assets.

No `PlatformPayload` is inserted into the current Tool result, and no sender is
connected in this Sprint.
