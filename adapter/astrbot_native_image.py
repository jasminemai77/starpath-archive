"""Small AstrBot-native component builder for an already prepared local image."""

from __future__ import annotations

from ..experience.delivery import PreparedAstrBotResource


def build_native_image_component(prepared: PreparedAstrBotResource):
    """Create one AstrBot image component; delivery remains owned by the event pipeline."""
    import astrbot.api.message_components as Comp

    return Comp.Image.fromFileSystem(str(prepared.resolved_path))


def build_native_smoke_chain(prepared: PreparedAstrBotResource) -> list[object]:
    """Build the labelled development smoke chain with AstrBot-native components."""
    import astrbot.api.message_components as Comp

    return [
        Comp.Plain("[DEV] Starpath native image smoke: manifest asset resolved."),
        Comp.Image.fromFileSystem(str(prepared.resolved_path)),
    ]
