# AstrBot runtime integration test guide

This guide verifies the plugin boundary in a local AstrBot instance. It does
not claim that a QQ or other live IM-platform test has been performed.

## Environment requirements

- AstrBot `>=4.27.2` with Native Agent tool calling enabled.
- Python `>=3.12` for the current AstrBot CLI installation path.
- Git and network access to clone this repository.
- A configured local chat channel or the AstrBot WebUI chat for the message
  test. QQ is optional and not required for this guide.

## Installation

Run these commands from an empty AstrBot working directory:

```powershell
uv tool install astrbot --python 3.12
astrbot init
git clone https://github.com/jasminemai77/starpath-archive.git data/plugins/starpath_plugin
astrbot plug list
```

The plugin list should include `starpath_plugin`. Configure a model provider
and a local chat channel in AstrBot before testing Agent tool calls.

## Start command

```powershell
astrbot run --reload
```

`--reload` is useful during local plugin development. For later ordinary
starts, use `astrbot run`.

## Plugin test commands

Run the repository's isolated tests from the cloned plugin directory:

```powershell
cd data/plugins/starpath_plugin
python -m pytest -q
python -m ruff check .
```

## Message test flow

1. Open the configured local chat channel or AstrBot WebUI chat.
2. Send: `请调用 generate_starpath_record，生成今天的星轨记录。`
3. Inspect the Agent tool trace or runtime log for a call to
   `generate_starpath_record`.
4. Inspect the tool result before the Native Agent's final response.

## Expected tool result

The tool result is JSON with exactly these top-level keys:

```text
record_id, generated_at, mode, spread, star, tarot, quote, metadata
```

`generated_at` uses UTC ISO 8601 format. `metadata.content_scope` is
`symbolic_entertainment`; it is a machine-readable boundary marker, not a
user-facing reply. The Native Agent—not this plugin—produces any final chat
message.

## Scope and evidence

The repository test suite includes an AstrBot API-stub integration simulation,
not a live AstrBot process or QQ account. Run the steps above to produce local
runtime evidence for your own Agent and channel configuration.

For current CLI behavior, see AstrBot's official
[CLI documentation](https://docs.astrbot.app/en/use/cli.html).
