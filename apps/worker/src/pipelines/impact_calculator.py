"""Asset impact calculation: event → AssetImpact rows (rule-based first, LLM when uncertain)."""

import json
import logging
import os

from sqlalchemy import delete, func, or_, select

from core.database import async_session_factory
from core.redis_client import QUEUE_JOBS, get_redis
from models.asset import Asset
from models.asset_impact import AssetImpact
from models.event import Event
from pipelines.impact_rules import (
    MAX_CANDIDATE_ASSETS,
    compute_impacts,
    get_rules_for_event,
)
from pipelines.prompts.impact_calculator import IMPACT_CALCULATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.6
VALID_DIRECTIONS = frozenset({"up", "down", "neutral"})


def _candidate_asset_types_from_rules(rules: list) -> set[str] | None:
    """
    From rule entries, collect asset_type set. None means "all types" (any entry has None/"*").
    """
    types: set[str] = set()
    for e in rules:
        at = e.get("asset_type")
        if at is None or (isinstance(at, str) and (at.strip().lower() in ("", "*"))):
            return None
        types.add(at.strip().lower())
    return types


def _is_uncertain(
    event_type: str,
    confidence: float | None,
    used_default_rules: bool,
) -> bool:
    """True if we should use LLM for impact (policy_change, low confidence, or no specific rule)."""
    if used_default_rules:
        return True
    if event_type == "policy_change":
        return True
    conf = float(confidence or 0.5)
    return conf < CONFIDENCE_THRESHOLD


def _call_llm_impacts(
    event_type: str,
    impact_type: str,
    source_summary: str | None,
    confidence: float | None,
    asset_types: list[str],
) -> list[dict] | None:
    """
    Call OpenAI for per-asset_type direction and strength.
    Returns list of { "asset_type", "direction", "strength" } or None on skip/failure.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.debug("Impact calculator LLM skip: OPENAI_API_KEY not set")
        return None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    summary = (source_summary or "").strip()[:2000] or "(no summary)"
    conf = float(confidence or 0.5)
    conf = max(0.0, min(1.0, conf))
    types_str = ", ".join(sorted(set(asset_types))) if asset_types else "unknown"
    user_content = (
        f"event_type: {event_type}\nimpact_type: {impact_type}\n"
        f"confidence: {conf}\n\nEvent summary:\n{summary}\n\n"
        f"Asset types to assess: {types_str}\n\n"
        "Output a JSON object with key 'impacts' (array of { asset_type, direction, strength })."
    )
    try:
        from openai import OpenAI

        logger.info(
            "Impact calculator calling LLM model=%s event_id context",
            model,
        )
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": IMPACT_CALCULATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            max_tokens=512,
        )
        raw = response.choices[0].message.content
        if not raw:
            logger.warning("Impact calculator LLM returned empty content")
            return None
        data = json.loads(raw)
        impacts = data.get("impacts")
        if not isinstance(impacts, list):
            logger.warning("Impact calculator LLM missing or invalid impacts array")
            return None
        result = []
        for item in impacts:
            if not isinstance(item, dict):
                continue
            at = (item.get("asset_type") or "").strip().lower()
            if not at:
                continue
            direction = (item.get("direction") or "neutral").strip().lower()
            if direction not in VALID_DIRECTIONS:
                direction = "neutral"
            strength = item.get("strength")
            if isinstance(strength, (int, float)):
                strength = max(0.0, min(1.0, float(strength)))
            else:
                strength = 0.25
            result.append({"asset_type": at, "direction": direction, "strength": strength})
        if not result:
            logger.warning("Impact calculator LLM returned no valid impacts")
            return None
        logger.info("Impact calculator LLM result count=%s", len(result))
        return result
    except Exception as e:
        logger.warning("Impact calculator LLM failed: %s", e, exc_info=True)
        return None


def _apply_llm_impacts_to_assets(
    llm_impacts: list[dict],
    assets: list[dict],
    event_country_id: int | None,
    confidence: float | None,
) -> list[dict]:
    """
    Map LLM impacts (per asset_type) to per-asset rows.
    Returns list of { "asset_id", "direction", "strength" }.
    """
    by_type: dict[str, dict] = {e["asset_type"]: e for e in llm_impacts}
    conf = max(0.0, min(1.0, float(confidence or 0.5)))
    result = []
    for asset in assets:
        asset_id = asset["id"]
        asset_type = (asset.get("asset_type") or "").strip().lower() or "unknown"
        asset_country_id = asset.get("country_id")
        entry = by_type.get(asset_type)
        if entry:
            direction = entry["direction"]
            base_strength = entry["strength"]
        else:
            direction = "neutral"
            base_strength = 0.25
        if event_country_id is not None and asset_country_id is not None:
            country_factor = 1.0 if event_country_id == asset_country_id else 0.7
        else:
            country_factor = 1.0
        strength = base_strength * conf * country_factor
        strength = max(0.0, min(1.0, round(strength, 4)))
        result.append({"asset_id": asset_id, "direction": direction, "strength": strength})
    return result


async def run_impact_calculation(event_id: int) -> None:
    """
    Load event, get rules, query candidate assets. Compute impacts by rules;
    when uncertain (default rules / policy_change / low confidence), use LLM.
    Save AssetImpact rows, then enqueue impact_computed for downstream.
    """
    logger.info("Running impact calculation for event_id=%s", event_id)
    async with async_session_factory() as session:
        # 1. Load event (include source_summary for LLM)
        stmt = select(
            Event.id,
            Event.event_type,
            Event.country_id,
            Event.impact_type,
            Event.confidence,
            Event.source_summary,
        ).where(Event.id == event_id)
        r = await session.execute(stmt)
        row = r.one_or_none()
        if not row:
            logger.warning("Event not found event_id=%s; skip impact calculation", event_id)
            return

        event_type = row.event_type or "unknown"
        country_id = row.country_id
        impact_type = row.impact_type
        confidence = row.confidence
        source_summary = getattr(row, "source_summary", None)

        # 2. Remove existing impacts for this event (idempotent recalc)
        await session.execute(delete(AssetImpact).where(AssetImpact.event_id == event_id))

        # 3. Rules for this event
        rules, used_default_rules = get_rules_for_event(event_type, impact_type)
        asset_types = _candidate_asset_types_from_rules(rules)

        # 4. Candidate assets query
        q = (
            select(Asset.id, Asset.asset_type, Asset.country_id)
            .limit(MAX_CANDIDATE_ASSETS)
        )
        if country_id is not None:
            q = q.where(
                or_(
                    Asset.country_id == country_id,
                    Asset.country_id.is_(None),
                )
            )
        if asset_types is not None:
            q = q.where(func.lower(Asset.asset_type).in_(asset_types))

        r = await session.execute(q)
        rows = r.all()
        if not rows:
            logger.warning("No candidate assets for event_id=%s; skip impact calculation", event_id)
            return

        assets = [
            {"id": row.id, "asset_type": row.asset_type, "country_id": row.country_id}
            for row in rows
        ]
        event_dict = {
            "event_type": event_type,
            "country_id": country_id,
            "impact_type": impact_type,
            "confidence": confidence,
        }

        # 5. Compute impacts: rules first; if uncertain, try LLM and replace on success
        impacts_data = compute_impacts(event_dict, assets, rules)
        if _is_uncertain(event_type, confidence, used_default_rules):
            unique_asset_types = list(
                {(a.get("asset_type") or "").strip().lower() or "unknown" for a in assets}
            )
            llm_impacts = _call_llm_impacts(
                event_type,
                impact_type or "market",
                source_summary,
                confidence,
                unique_asset_types,
            )
            if llm_impacts:
                impacts_data = _apply_llm_impacts_to_assets(
                    llm_impacts, assets, country_id, confidence
                )
                logger.debug(
                    "Using LLM impacts for event_id=%s count=%s",
                    event_id, len(impacts_data),
                )
            else:
                logger.debug("LLM skipped or failed; using rule impacts for event_id=%s", event_id)
        else:
            logger.debug("Computed %s impacts for event_id=%s (rules)", len(impacts_data), event_id)

        # 6. Save AssetImpact rows
        for row in impacts_data:
            impact = AssetImpact(
                event_id=event_id,
                asset_id=row["asset_id"],
                direction=row["direction"],
                strength=row["strength"],
            )
            session.add(impact)
        await session.commit()
        logger.info("Saved %s asset impacts for event_id=%s", len(impacts_data), event_id)

    # 7. Enqueue for downstream
    redis = get_redis()
    try:
        payload = json.dumps({"type": "impact_computed", "event_id": event_id})
        await redis.lpush(QUEUE_JOBS, payload)
        logger.info("Enqueued impact_computed event_id=%s", event_id)
    finally:
        await redis.aclose()
