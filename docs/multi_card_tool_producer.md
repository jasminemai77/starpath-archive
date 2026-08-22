# Future Multi-Card Tool Producer

Sprint 3D-5.4 introduces `StarpathToolV2Producer`, a pure, unregistered
builder for valid `starpath.tool.v2` result dictionaries.  It adds generation
capability only; it does not expose a new Native Tool or alter the stable
`generate_starpath_record` v1 registration.

## Producer boundary

```text
Star + Quote + injected TarotDrawProvider
  -> StarpathToolV2Producer
  -> schema-validated starpath.tool.v2 dictionary
```

The producer does not resolve assets, create presentations, send a message,
read chat state, or contain AstrBot/QQ/Runtime code.

## Injected selection policy

The constructor accepts a `TarotDrawProvider` with one method:

```python
def draw() -> TarotDraw: ...
```

The producer calls it once for `single`, or three times for `three_card`.
This keeps draw policy separate from Tool result structure: a future caller can
use random selection, a fixed test sequence, or another approved source
without modifying the producer.

## Supported output shapes

- `single`: one card, `position="main"`, `order=0`
- `three_card`: three cards in `past`/`present`/`future` order, with orders
  `0`/`1`/`2`

Each card preserves the complete existing `TarotDraw` data and adds only the
v2 position/order fields.  The producer validates every generated payload via
the platform-neutral `FutureStarpathToolV2Parser` before returning it.

## v1 isolation

The v1 Tool registration, `StarpathToolAdapter`, `StarpathExperience`, and
`StarpathService` are untouched.  A future, separately approved integration
must decide whether and how to expose this builder through a Native Tool; this
Sprint intentionally does not activate v2 Agent calls.
