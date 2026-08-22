# Agent Multi-Card Capability

Sprint 3D-5.5 exposes a second Native Agent Tool while preserving the existing
v1 entry unchanged.

| Tool | Supported spread | Contract |
| --- | --- | --- |
| `generate_starpath_record` | `single` | `starpath.tool.v1` |
| `generate_starpath_spread` | `single`, `three_card` | `starpath.tool.v2` |

The Native Agent selects the v2 Tool and supplies `spread` explicitly.  The
plugin does not inspect user text or infer a spread.  `mode` remains `daily`.

`generate_starpath_spread` delegates to the injectable v2 producer through a
separate adapter.  Its result is schema-validated `starpath.tool.v2` JSON; it
does not resolve images, generate final chat text, send messages, or use QQ or
Runtime APIs.

The v1 Tool remains the compatibility path for existing single-card callers.
The v2 Tool is a new capability, not a replacement or changed meaning of v1.
