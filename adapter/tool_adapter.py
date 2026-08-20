"""Convert AstrBot tool calls to core service inputs and structured JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from ..core import StarpathService, ValidationError


class StarpathToolAdapter:
    """A narrow adapter that never reads message content or chat history."""

    def __init__(self, service: StarpathService) -> None:
        self._service = service

    async def generate(self, event: Any, mode: str = "daily", spread: str = "single") -> str:
        try:
            record = self._service.generate(
                user_hash=self._event_user_hash(event),
                on_date=datetime.now(timezone.utc).date(),
                mode=mode,
                spread=spread,
            )
        except ValidationError as exc:
            return json.dumps(
                {"error": "INVALID_PARAMETERS", "reason": str(exc)}, ensure_ascii=False
            )
        return json.dumps(record.as_dict(), ensure_ascii=False)

    @staticmethod
    def _event_user_hash(event: Any) -> str:
        """Hash only AstrBot's sender identifier; do not inspect message text/history."""
        get_sender_id = getattr(event, "get_sender_id", None)
        if not callable(get_sender_id):
            raise ValidationError("sender identifier is unavailable")
        sender_id = get_sender_id()
        if sender_id is None or not str(sender_id).strip():
            raise ValidationError("sender identifier is unavailable")
        return sha256(str(sender_id).encode("utf-8")).hexdigest()
