"""Assemble a machine-readable experience contract without chat generation."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models import StarpathRecord


class StarpathExperience:
    """Organize domain data for a Native Agent; never produce final chat prose."""

    CONTRACT_VERSION = "starpath.tool.v1"

    def organize(
        self,
        record: StarpathRecord,
        *,
        generated_at: datetime,
        mode: str,
        spread: str,
    ) -> dict[str, object]:
        """Return the complete structured tool contract for one record."""
        generated_at_utc = generated_at.astimezone(timezone.utc)
        return {
            "record_id": record.record_id,
            "generated_at": generated_at_utc.isoformat().replace("+00:00", "Z"),
            "mode": mode,
            "spread": spread,
            "star": record.as_dict()["star"],
            "tarot": record.tarot.as_dict(),
            "quote": {
                "id": record.quote.id,
                "text": record.quote.text,
                "theme": record.quote.theme,
            },
            "metadata": {
                "contract_version": self.CONTRACT_VERSION,
                "content_scope": "symbolic_entertainment",
                "generation_timezone": "UTC",
                "experience": {
                    "star_type": record.star.type,
                    "tarot_arcana": record.tarot.card.arcana,
                    "tarot_orientation": record.tarot.orientation,
                    "quote_theme": record.quote.theme,
                },
            },
        }
