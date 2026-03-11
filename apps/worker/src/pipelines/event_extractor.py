"""Event extractor stub: text → Event attributes for DB."""

from datetime import datetime, timezone


def extract_events(
    text: str,
    *,
    occurred_at: datetime | None = None,
) -> list[dict]:
    """
    Extract event attributes from text. Stub: returns one synthetic event per call.
    Input: raw text (e.g. news body). Output: list of dicts with keys
    event_type, country_id, actor, impact_type, occurred_at, source_summary, confidence.
    """
    if not text or not text.strip():
        return []
    ts = occurred_at or datetime.now(timezone.utc)
    summary = (text.strip()[:500] + "…") if len(text.strip()) > 500 else text.strip()
    return [
        {
            "event_type": "policy_change",
            "country_id": None,
            "actor": None,
            "impact_type": "market",
            "occurred_at": ts,
            "source_summary": summary,
            "confidence": 0.5,
            "metadata_": {"stub": True},
        }
    ]
