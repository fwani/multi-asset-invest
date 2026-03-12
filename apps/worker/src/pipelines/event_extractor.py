"""Event extractor: text → Event attributes (rule-based first, LLM fallback when uncertain)."""

import json
import logging
import os
from datetime import datetime, timezone

from pipelines.prompts.event_extractor import EVENT_EXTRACTOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Confidence below this triggers LLM fallback (or policy_change fallback counts as uncertain)
CONFIDENCE_THRESHOLD = 0.6

# event_type in detection order (more specific first)
EVENT_TYPE_PATTERNS: list[tuple[str, list[str], float]] = [
    (
        "rate_hike",
        [
            "rate hike", "interest rate increase", "rates raised", "hiked rates",
            "금리 인상", "fed raises", "ecb raises", "raises interest",
        ],
        0.8,
    ),
    (
        "rate_cut",
        [
            "rate cut", "interest rate cut", "rates cut", "cut rates",
            "금리 인하", "fed cuts", "ecb cuts", "cuts interest",
        ],
        0.8,
    ),
    ("inflation", ["inflation", "inflationary", "cpi", "물가", "consumer prices"], 0.7),
    (
        "recession_risk",
        ["recession", "경기 침체", "slowdown", "economic contraction", "gdp decline"],
        0.7,
    ),
    (
        "geopolitical",
        ["war", "sanctions", "지정학", "conflict", "military", "invasion", "nato"],
        0.7,
    ),
    ("policy_change", ["policy", "regulation", "정책", "central bank", "government"], 0.55),
]

# keyword (lower) -> country code (ISO 2-letter). Order: longer/more specific first when scanning.
COUNTRY_KEYWORDS: list[tuple[str, str]] = [
    ("federal reserve", "US"),
    ("fed ", "US"),
    (" fed", "US"),
    ("usa", "US"),
    ("u.s.", "US"),
    ("united states", "US"),
    ("미국", "US"),
    ("ecb", "EU"),
    ("european central bank", "EU"),
    ("유럽중앙은행", "EU"),
    ("euro zone", "EU"),
    ("eu ", "EU"),
    (" eu", "EU"),
    ("boj", "JP"),
    ("bank of japan", "JP"),
    ("일본", "JP"),
    ("japan", "JP"),
    ("pboc", "CN"),
    ("people's bank of china", "CN"),
    ("중국", "CN"),
    ("china", "CN"),
    ("uk ", "GB"),
    (" uk", "GB"),
    ("bank of england", "GB"),
    ("brexit", "GB"),
]

# actor display name (first match used)
ACTOR_KEYWORDS: list[tuple[str, str]] = [
    ("federal reserve", "Federal Reserve"),
    ("fed ", "Fed"),
    ("ecb", "ECB"),
    ("european central bank", "ECB"),
    ("boj", "BOJ"),
    ("bank of japan", "BOJ"),
    ("pboc", "PBOC"),
    ("people's bank of china", "PBOC"),
    ("bank of england", "Bank of England"),
    ("government", "Government"),
    ("정부", "Government"),
]

VALID_EVENT_TYPES = frozenset(
    {"rate_hike", "rate_cut", "policy_change", "geopolitical", "inflation", "recession_risk"}
)


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _extract_by_rules(text: str) -> tuple[str, str | None, str | None, float]:
    """Return (event_type, country_code, actor, confidence)."""
    norm = _normalize(text)
    event_type = "policy_change"
    confidence = 0.5

    for et, patterns, base_conf in EVENT_TYPE_PATTERNS:
        for p in patterns:
            if p.lower() in norm:
                event_type = et
                confidence = base_conf
                break
        if event_type != "policy_change":
            break

    country_code: str | None = None
    for keyword, code in COUNTRY_KEYWORDS:
        if keyword in norm:
            country_code = code
            break

    actor: str | None = None
    for keyword, name in ACTOR_KEYWORDS:
        if keyword in norm:
            actor = name
            break

    return event_type, country_code, actor, confidence


def _is_uncertain(event_type: str, confidence: float) -> bool:
    return event_type == "policy_change" or confidence < CONFIDENCE_THRESHOLD


def _call_llm(text: str) -> tuple[dict | None, str | None]:
    """Call OpenAI for event_type, country_code, actor, confidence.
    Returns (result_dict or None, model_name or None) on skip/failure."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.debug("Event extractor LLM skip: OPENAI_API_KEY not set")
        return None, None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    truncated = text.strip()[:3000] if text else ""

    try:
        from openai import OpenAI

        logger.info("Event extractor calling LLM model=%s input_len=%s", model, len(truncated))
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EVENT_EXTRACTOR_SYSTEM_PROMPT},
                {"role": "user", "content": truncated or "(no content)"},
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
        )
        raw = response.choices[0].message.content
        if not raw:
            logger.warning("Event extractor LLM returned empty content")
            return None, model
        data = json.loads(raw)
        et = (data.get("event_type") or "").strip().lower().replace("-", "_")
        if et not in VALID_EVENT_TYPES:
            et = "policy_change"
        cc = data.get("country_code")
        if cc is not None and isinstance(cc, str):
            cc = cc.strip().upper()[:2] or None
        else:
            cc = None
        actor = data.get("actor")
        if actor is not None and isinstance(actor, str):
            actor = actor.strip()[:255] or None
        else:
            actor = None
        conf = data.get("confidence")
        if isinstance(conf, (int, float)):
            conf = max(0.0, min(1.0, float(conf)))
        else:
            conf = 0.6
        logger.info(
            "Event extractor LLM result event_type=%s country_code=%s actor=%s confidence=%s",
            et, cc, actor, conf,
        )
        return {"event_type": et, "country_code": cc, "actor": actor, "confidence": conf}, model
    except Exception as e:
        logger.warning("Event extractor LLM failed: %s", e, exc_info=True)
        return None, model


def extract_events(
    text: str,
    *,
    occurred_at: datetime | None = None,
) -> list[dict]:
    """
    Extract event attributes from text. Rule-based first; if uncertain, call OpenAI.
    Returns list of dicts with keys: event_type, country_id, country_code, actor,
    impact_type, occurred_at, source_summary, confidence, metadata_.
    """
    if not text or not text.strip():
        return []
    ts = occurred_at or datetime.now(timezone.utc)
    raw = text.strip()
    summary = (raw[:500] + "…") if len(raw) > 500 else raw

    event_type, country_code, actor, confidence = _extract_by_rules(text)

    metadata: dict = {"extraction_source": "rules"}
    llm_model: str | None = None

    if _is_uncertain(event_type, confidence):
        logger.debug(
            "Event extractor uncertain (rule event_type=%s confidence=%s), trying LLM",
            event_type, confidence,
        )
        llm_result, llm_model = _call_llm(text)
        if llm_result:
            metadata["extraction_source"] = "llm"
            if llm_model:
                metadata["llm_model"] = llm_model
            event_type = llm_result.get("event_type", event_type)
            if llm_result.get("country_code") is not None:
                country_code = llm_result["country_code"]
            if llm_result.get("actor") is not None:
                actor = llm_result["actor"]
            confidence = llm_result.get("confidence", confidence)
        else:
            logger.debug("Event extractor using rule result (LLM skipped or failed)")
            metadata["llm_attempted"] = True
    else:
        logger.debug("Event extractor rule result confident event_type=%s", event_type)

    return [
        {
            "event_type": event_type,
            "country_id": None,
            "country_code": country_code,
            "actor": actor,
            "impact_type": "market",
            "occurred_at": ts,
            "source_summary": summary,
            "confidence": confidence,
            "metadata_": metadata,
        }
    ]
