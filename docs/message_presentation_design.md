# Message Presentation Model

## Purpose

`MessagePresentation` is the platform-neutral representation of one complete
Starpath experience. It separates message composition from the current
single-response `PresentationResult` plan, so richer readings can be organised
without coupling business data to a delivery platform.

## Model

`MessagePresentation` contains:

- `title`: required experience heading;
- `subtitle`: optional short context line;
- `sections`: ordered `MessageSection` text blocks;
- `resources`: existing `DisplayResource` references, with no duplicate image
  model;
- `footer`: optional short closing line.

Each `MessageSection` has a required `title`, required `content`, and unique
non-negative `order`. The model normalises sections into order sequence.
An empty resource tuple is valid for a text-only degradation.

## Compatibility

`PresentationResultMessageConverter` performs a one-way conversion from the
existing `PresentationResult`. Its title becomes the message title, the legacy
title section is omitted to avoid duplication, legacy text sections retain
their order, and every `ImagePresentation.resource` is retained by identity.

The existing `ExperienceResult`, `PresentationResult`, `PresentationConsumer`,
and runtime delivery boundaries are unchanged. Current consumers may continue
using `PresentationResult`; future surfaces may opt into `MessagePresentation`.

## Future Consumers

The model deliberately does not implement delivery. A future adapter can turn
one message model into:

- a QQ forward-message grouping;
- a Web experience view;
- a Discord embed or ordered attachment set.

Those adapters must decide their own platform payloads and delivery behaviour.
This model does not import AstrBot, QQ, OneBot, NapCat, or runtime components.
