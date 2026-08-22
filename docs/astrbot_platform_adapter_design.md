# AstrBot Platform Adapter Design

## Overview

`AstrBotAdapter` is the AstrBot-specific implementation of the generic
`PlatformAdapter` boundary. It accepts a platform-neutral `DisplayResource`,
creates a transport-free `AstrBotImagePayload`, and exposes the result as the
existing generic `PlatformPayload` contract.

This is a design-level payload adapter only. It does not import an AstrBot
message object, call a send API, open an image, upload a file, create a CDN
reference, or modify an event flow.

## Architecture Position

```text
AssetReference
  -> AssetReference Consumer
  -> DisplayResource
  -> AstrBotAdapter
  -> AstrBotImagePayload
  -> PlatformPayload
  -> future AstrBot Runtime sender
```

AstrBot appears only at the adapter boundary. Resolver, Manifest Provider, and
Asset Consumer remain platform-neutral. The adapter is a `PlatformAdapter`
implementation, not an alternative resource-resolution path.

## Adapter Responsibility

`AstrBotAdapter` is responsible for validating generic image display metadata
and describing it as an `AstrBotImagePayload`. It then normalizes that
intermediate representation to `PlatformPayload` so callers retain the stable
generic interface.

It is not responsible for card lookup, manifest parsing, asset file access,
image decoding, image upload, Base64 conversion, message construction, event
access, user data, or delivery. The adapter has no `send()` operation.

## Payload Design

```python
AstrBotImagePayload(
    type="image",
    resource="major/17_the_star.png",
    metadata={
        "deck_id": "dark_cosmic_archive",
        "card_id": "major-17",
    },
)
```

| Field | Meaning |
| --- | --- |
| `type` | Intermediate AstrBot resource category, currently `image`. |
| `resource` | Package-relative resource reference; never image bytes, a URI upload result, or a message object. |
| `metadata` | Preserved display metadata such as deck, card, asset key, and version. |

`AstrBotImagePayload.as_platform_payload()` returns a generic
`PlatformPayload` with `payload_type="image"`, the same resource reference in
`content`, and `target_platform="astrbot"` metadata. It does not add an
AstrBot SDK type to the public core contracts.

## Runtime Boundary

```text
DisplayResource
  -> AstrBotAdapter (conversion only)
  -> AstrBotImagePayload / PlatformPayload
  -> AstrBot Runtime (future resource access and delivery)
  -> platform send
```

The Runtime owns actual resource handling and delivery after a separately
approved integration. It may decide how to turn the reference into a native
message object, whether to upload it, and how to report delivery errors. This
Sprint neither invokes nor changes Runtime code.

## Error Handling

| Condition | Error |
| --- | --- |
| Non-image resource type | `UnsupportedAstrBotResourceError` |
| Missing resource reference or non-PNG format | `InvalidPlatformPayloadError` |
| Malformed intermediate metadata | `AstrBotPayloadBuildError` |

All errors derive from `AdapterConversionError` and are explicit. There is no
fallback message, implicit file read, or silent send failure.

## Future Extension

AstrBot is one `PlatformAdapter` implementation. Future Web, Discord,
Telegram, and CLI adapters can convert the same `DisplayResource` without
changing the Tarot Domain, Resolver, Manifest Provider, or Asset Consumer.

A later AstrBot Runtime integration may consume `AstrBotImagePayload`, but it
must remain downstream of the adapter and preserve the existing Tool Contract.

## Compatibility Notes

This design does not change:

- Tool Contract fields, message structure, Agent permissions, or user flow.
- Runtime code or existing AstrBot Native Tool entry point.
- Tarot Domain, Resolver, Manifest Provider, or Asset Consumer APIs.
- Visual metadata, PNG files, or candidate history.

No payload is added to the current tool response and no AstrBot sending API is
called in this Sprint.
