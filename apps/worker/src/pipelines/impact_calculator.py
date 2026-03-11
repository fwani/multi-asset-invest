"""Asset impact calculation step (rule stub): event → AssetImpact rows, then enqueue."""

import json
import logging

from sqlalchemy import select

from core.database import async_session_factory
from core.redis_client import QUEUE_JOBS, get_redis
from models.asset import Asset
from models.asset_impact import AssetImpact

logger = logging.getLogger(__name__)

# Stub: max assets to create impacts for per event
STUB_MAX_ASSETS = 5
# Stub: direction cycle for variety
STUB_DIRECTIONS = ("up", "down", "neutral")
# Stub: strength range
STUB_STRENGTH_MIN, STUB_STRENGTH_MAX = 0.3, 0.9


def compute_impacts_stub(event_id: int, asset_ids: list[int]) -> list[dict]:
    """
    Stub rule: for each asset_id return direction and strength.
    Real implementation would use event attributes + asset metadata.
    """
    result = []
    for i, asset_id in enumerate(asset_ids):
        direction = STUB_DIRECTIONS[i % len(STUB_DIRECTIONS)]
        # Simple stub strength
        strength = STUB_STRENGTH_MIN + (i % 3) * 0.2
        result.append({
            "asset_id": asset_id,
            "direction": direction,
            "strength": min(max(strength, 0), 1.0),
        })
    return result


async def run_impact_calculation(event_id: int) -> None:
    """
    Load event (existence check), get asset ids from DB, compute impacts (stub),
    save AssetImpact rows, then enqueue impact_computed for downstream (e.g. signal).
    """
    logger.info("Running impact calculation for event_id=%s", event_id)
    async with async_session_factory() as session:
        # Resolve asset ids (stub: first N assets)
        stmt = select(Asset.id).limit(STUB_MAX_ASSETS)
        r = await session.execute(stmt)
        asset_ids = [row[0] for row in r.all()]
        if not asset_ids:
            logger.warning("No assets in DB; skip impact calculation for event_id=%s", event_id)
            return
        logger.debug("Found %s assets for impact calculation (event_id=%s)", len(asset_ids), event_id)

        impacts_data = compute_impacts_stub(event_id, asset_ids)
        logger.debug("Computed %s impacts for event_id=%s", len(impacts_data), event_id)
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

    # Enqueue for downstream (e.g. signal generator)
    redis = get_redis()
    try:
        payload = json.dumps({"type": "impact_computed", "event_id": event_id})
        await redis.lpush(QUEUE_JOBS, payload)
        logger.info("Enqueued impact_computed event_id=%s", event_id)
    finally:
        await redis.aclose()
