"""Minimal local-file implementation of the prepare-only runtime boundary."""

from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath

from ...adapter.astrbot_platform import AstrBotImagePayload
from .errors import (
    InvalidRuntimeResourceError,
    RuntimePayloadPreparationError,
    RuntimeResourceAccessError,
    RuntimeResourceNotFoundError,
)
from .interface import RuntimeImageDelivery
from .models import PreparedAstrBotResource


class LocalRuntimeImageDelivery(RuntimeImageDelivery):
    """Prepare PNG files rooted under one injected local deck asset directory."""

    def __init__(self, asset_root: str | Path) -> None:
        self._asset_root = Path(asset_root)

    def prepare(self, payload: AstrBotImagePayload) -> PreparedAstrBotResource:
        """Validate and resolve a payload reference without opening or sending the file."""
        self._validate_payload(payload)
        target = self._resolve_resource(payload.resource)
        return PreparedAstrBotResource(
            resource_type=payload.type,
            resolved_path=str(target),
            media_type="image/png",
            metadata=dict(payload.metadata),
        )

    @staticmethod
    def _validate_payload(payload: AstrBotImagePayload) -> None:
        if not isinstance(payload, AstrBotImagePayload):
            raise RuntimePayloadPreparationError("Expected an AstrBotImagePayload")
        if payload.type != "image":
            raise RuntimePayloadPreparationError(
                "Only image payloads can enter runtime preparation"
            )
        if not isinstance(payload.resource, str) or not payload.resource:
            raise RuntimePayloadPreparationError("An image resource reference is required")
        if not isinstance(payload.metadata, dict):
            raise RuntimePayloadPreparationError("Payload metadata must be a dictionary")

    def _resolve_resource(self, reference: str) -> Path:
        relative_path = self._safe_relative_path(reference)
        try:
            root = self._asset_root.resolve()
            if not root.is_dir():
                raise RuntimeResourceAccessError("Configured runtime asset root is not a directory")
            target = (root / Path(*relative_path.parts)).resolve()
            try:
                target.relative_to(root)
            except ValueError as error:
                raise InvalidRuntimeResourceError(
                    "Resolved resource must remain inside the runtime asset root"
                ) from error
            if not target.exists():
                raise RuntimeResourceNotFoundError(f"Runtime resource was not found: {reference}")
            if not target.is_file():
                raise InvalidRuntimeResourceError("Runtime resource must be a regular file")
            return target
        except RuntimeResourceNotFoundError:
            raise
        except RuntimeResourceAccessError:
            raise
        except OSError as error:
            raise RuntimeResourceAccessError(
                "Runtime resource could not be accessed safely"
            ) from error

    @staticmethod
    def _safe_relative_path(reference: str) -> PurePosixPath:
        relative_path = PurePosixPath(reference)
        if (
            relative_path.is_absolute()
            or PureWindowsPath(reference).is_absolute()
            or ".." in relative_path.parts
            or "\\" in reference
            or relative_path.suffix.lower() != ".png"
        ):
            raise InvalidRuntimeResourceError(
                "Runtime image resource must be a package-relative PNG reference"
            )
        return relative_path
