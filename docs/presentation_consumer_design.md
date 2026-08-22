# Presentation Consumer Contract

## Overview

The Presentation Consumer converts a platform-neutral `PresentationResult` to
an ordered `PlatformPresentation`. It is a conversion boundary only: a runtime
owns component construction, media preparation, and delivery.

## Current Architecture

```text
ExperienceResult -> PresentationBuilder -> PresentationResult
  -> PresentationConsumer -> PlatformPresentation -> future platform runtime
```

## Consumer Responsibility

`PresentationConsumer.consume()` maps `TextPresentation` to `TextElement` and
`ImagePresentation` to `ResourceElement`. A resource element retains the same
`DisplayResource` reference; it does not open, encode, upload, or mutate it.

## Platform Boundary

`PlatformPresentation` contains only title, mode, and ordered neutral
elements. It contains no SDK component, transport message, protocol payload,
or platform identifier.

## Data Flow

Text sections preserve `section_id`, title, and content. Image sections become
resource elements. Unknown section types fail explicitly rather than being
silently omitted.

## Error Handling

`InvalidPresentationResultError` rejects an invalid root input;
`UnsupportedPresentationSectionError` rejects an unknown section; both inherit
`PresentationConversionError`.

## Future Platform Consumers

Future consumers may consume `PlatformPresentation` for a web renderer or a
platform adapter, but should not change this contract. They must keep resource
delivery outside this conversion layer.

## AstrBot Integration Plan

A separately authorized integration may turn `ResourceElement.resource` into
the existing AstrBot payload and runtime-prepared local resource. This contract
does not import AstrBot, invoke runtime delivery, construct a native component,
or send a message.
