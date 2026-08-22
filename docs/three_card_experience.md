# Three-Card Tarot Experience

Sprint 3D-5.2 enables the platform-neutral Experience layer to build an
ordered `three_card` reading.  It does not add a v2 Tool producer, modify the
stable `starpath.tool.v1` contract, or add QQ, AstrBot, Runtime, or delivery
behavior.

## Input shape

`TarotExperienceInput` accepts three `TarotCardSelection` values:

```python
TarotExperienceInput(
    deck_id="dark_cosmic_archive",
    spread="three_card",
    cards=(
        TarotCardSelection("major-00", "past", order=0),
        TarotCardSelection("major-01", "present", order=1),
        TarotCardSelection("major-02", "future", order=2),
    ),
)
```

The orchestrator validates the normalized order and exact shape:

1. `past`, order `0`
2. `present`, order `1`
3. `future`, order `2`

Optional `card_name` and `meaning` fields on a selection carry source-backed
card display data for the experience text.  If absent, the Experience layer
uses the stable card ID and explicitly states that no source-backed meaning was
provided; it does not generate an interpretation.

## Resolution and presentation

For each selection, the existing `AssetResolver` resolves `deck_id + card_id`,
then the existing `AssetReferenceConsumer` turns that result into a
`DisplayResource`.  No new image or platform resource logic was introduced.

The resulting `ExperienceResult` contains cards, resources, and sections in
Past / Present / Future order.  `ExperiencePresentationBuilder` keeps a card's
available image adjacent to its corresponding text section.  The existing
`PresentationResultMessageConverter` can therefore represent it as a
platform-neutral `MessagePresentation` with ordered sections and resources.

If one card asset is absent, three-card construction preserves all textual
Past / Present / Future sections and omits only that card's image.  Missing
decks and consumer failures remain explicit errors.  Single-card behavior,
including its existing missing-asset error behavior, remains unchanged.

## Deferred integration

This Sprint consumes only explicit `TarotExperienceInput` values.  A future
Sprint may connect an approved `starpath.tool.v2` producer/parser adapter to
this input.  That work remains separate from the v1 Tool and from delivery.
