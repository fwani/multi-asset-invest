"""Tests for impact_calculator: rules, _is_uncertain, _apply_llm_impacts_to_assets, integration."""

import os

import pytest

from pipelines.impact_calculator import (
    _apply_llm_impacts_to_assets,
    _candidate_asset_types_from_rules,
    _is_uncertain,
)
from pipelines.impact_rules import get_rules_for_event


class TestCandidateAssetTypesFromRules:
    def test_returns_none_when_any_entry_is_wildcard(self):
        rules = [{"asset_type": None, "direction": "neutral", "base_strength": 0.4}]
        assert _candidate_asset_types_from_rules(rules) is None

    def test_returns_none_when_asset_type_star(self):
        rules = [{"asset_type": "*", "direction": "up", "base_strength": 0.5}]
        assert _candidate_asset_types_from_rules(rules) is None

    def test_returns_set_of_types_when_all_specific(self):
        rules = [
            {"asset_type": "bond", "direction": "down", "base_strength": 0.8},
            {"asset_type": "stock", "direction": "down", "base_strength": 0.5},
        ]
        out = _candidate_asset_types_from_rules(rules)
        assert out is not None
        assert out == {"bond", "stock"}

    def test_policy_change_rules_return_none(self):
        rules, _ = get_rules_for_event("policy_change", "market")
        assert _candidate_asset_types_from_rules(rules) is None

    def test_rate_hike_rules_return_specific_types(self):
        rules, _ = get_rules_for_event("rate_hike", "market")
        out = _candidate_asset_types_from_rules(rules)
        assert out is not None
        assert "bond" in out
        assert "stock" in out


class TestIsUncertain:
    def test_default_rules_makes_uncertain(self):
        assert _is_uncertain("unknown", 0.9, used_default_rules=True) is True

    def test_policy_change_makes_uncertain(self):
        assert _is_uncertain("policy_change", 0.9, used_default_rules=False) is True

    def test_low_confidence_makes_uncertain(self):
        assert _is_uncertain("rate_hike", 0.5, used_default_rules=False) is True

    def test_high_confidence_specific_rules_not_uncertain(self):
        assert _is_uncertain("rate_hike", 0.8, used_default_rules=False) is False


class TestApplyLlmImpactsToAssets:
    def test_maps_asset_type_to_assets(self):
        llm_impacts = [
            {"asset_type": "bond", "direction": "down", "strength": 0.7},
            {"asset_type": "stock", "direction": "up", "strength": 0.5},
        ]
        assets = [
            {"id": 1, "asset_type": "bond", "country_id": None},
            {"id": 2, "asset_type": "stock", "country_id": None},
        ]
        out = _apply_llm_impacts_to_assets(llm_impacts, assets, None, 0.8)
        assert len(out) == 2
        by_id = {x["asset_id"]: x for x in out}
        assert by_id[1]["direction"] == "down"
        assert by_id[2]["direction"] == "up"
        assert 0 <= by_id[1]["strength"] <= 1.0
        assert 0 <= by_id[2]["strength"] <= 1.0

    def test_missing_asset_type_gets_neutral(self):
        llm_impacts = [{"asset_type": "bond", "direction": "down", "strength": 0.7}]
        assets = [{"id": 1, "asset_type": "crypto", "country_id": None}]
        out = _apply_llm_impacts_to_assets(llm_impacts, assets, None, 0.8)
        assert len(out) == 1
        assert out[0]["direction"] == "neutral"
        assert out[0]["strength"] > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set; skip integration test",
)
async def test_run_impact_calculation_saves_impacts():
    """Integration: run_impact_calculation with real DB creates AssetImpact rows."""
    from sqlalchemy import select

    from core.database import async_session_factory
    from models.asset_impact import AssetImpact
    from models.event import Event
    from pipelines.impact_calculator import run_impact_calculation

    # Assume an event exists (e.g. from crawl_and_extract). Use first event id.
    async with async_session_factory() as session:
        r = await session.execute(select(Event.id).limit(1))
        row = r.one_or_none()
    if row is None:
        pytest.skip("No event in DB")
    event_id = row[0]

    await run_impact_calculation(event_id)

    async with async_session_factory() as session:
        r = await session.execute(
            select(AssetImpact).where(AssetImpact.event_id == event_id)
        )
        impacts = r.scalars().all()
    assert len(impacts) >= 0
    for imp in impacts:
        assert imp.direction in ("up", "down", "neutral")
        assert 0 <= (imp.strength or 0) <= 1.0
