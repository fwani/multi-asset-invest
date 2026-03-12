"""Unit tests for impact_rules: get_rules_for_event, compute_impacts."""


from pipelines.impact_rules import (
    DEFAULT_RULES,
    IMPACT_RULES,
    compute_impacts,
    get_rules_for_event,
)


class TestGetRulesForEvent:
    def test_known_key_returns_rules(self):
        rules, used_default = get_rules_for_event("rate_hike", "market")
        assert used_default is False
        assert len(rules) > 0
        assert IMPACT_RULES[("rate_hike", "market")] == rules

    def test_unknown_returns_default(self):
        rules, used_default = get_rules_for_event("unknown_type", "sector")
        assert used_default is True
        assert rules == DEFAULT_RULES

    def test_normalizes_strip_lower(self):
        rules, used_default = get_rules_for_event("  RATE_HIKE  ", "  MARKET  ")
        assert used_default is False
        assert len(rules) > 0
        assert any(e.get("asset_type") == "bond" for e in rules)

    def test_none_impact_type_defaults_to_market(self):
        rules, _ = get_rules_for_event("policy_change", None)
        assert len(rules) == 1
        assert rules[0]["direction"] == "neutral"

    def test_fallback_to_market_impact(self):
        rules, used_default = get_rules_for_event("rate_hike", "sector")
        assert used_default is False
        assert len(rules) > 0
        assert rules == IMPACT_RULES[("rate_hike", "market")]


class TestComputeImpacts:
    def test_returns_one_entry_per_asset(self):
        event = {
            "event_type": "rate_hike",
            "country_id": None,
            "impact_type": "market",
            "confidence": 0.8,
        }
        assets = [
            {"id": 1, "asset_type": "bond", "country_id": None},
            {"id": 2, "asset_type": "stock", "country_id": None},
        ]
        rules, _ = get_rules_for_event("rate_hike", "market")
        out = compute_impacts(event, assets, rules)
        assert len(out) == 2
        assert {x["asset_id"] for x in out} == {1, 2}

    def test_bond_rate_hike_down(self):
        event = {
            "event_type": "rate_hike",
            "country_id": None,
            "impact_type": "market",
            "confidence": 1.0,
        }
        assets = [{"id": 1, "asset_type": "bond", "country_id": None}]
        rules, _ = get_rules_for_event("rate_hike", "market")
        out = compute_impacts(event, assets, rules)
        assert len(out) == 1
        assert out[0]["direction"] == "down"
        assert out[0]["strength"] > 0.5

    def test_strength_clamped_0_1(self):
        event = {
            "event_type": "rate_hike",
            "country_id": None,
            "impact_type": "market",
            "confidence": 2.0,
        }
        assets = [{"id": 1, "asset_type": "bond", "country_id": None}]
        rules, _ = get_rules_for_event("rate_hike", "market")
        out = compute_impacts(event, assets, rules)
        assert 0 <= out[0]["strength"] <= 1.0

    def test_country_match_increases_strength(self):
        event = {
            "event_type": "rate_hike",
            "country_id": 10,
            "impact_type": "market",
            "confidence": 0.8,
        }
        rules, _ = get_rules_for_event("rate_hike", "market")
        asset_same = [{"id": 1, "asset_type": "bond", "country_id": 10}]
        asset_other = [{"id": 2, "asset_type": "bond", "country_id": 20}]
        out_same = compute_impacts(event, asset_same, rules)
        out_other = compute_impacts(event, asset_other, rules)
        assert out_same[0]["strength"] > out_other[0]["strength"]

    def test_unknown_asset_type_gets_fallback_rule(self):
        event = {
            "event_type": "inflation",
            "country_id": None,
            "impact_type": "market",
            "confidence": 0.6,
        }
        assets = [{"id": 1, "asset_type": "unknown_asset", "country_id": None}]
        rules, _ = get_rules_for_event("inflation", "market")
        out = compute_impacts(event, assets, rules)
        assert len(out) == 1
        assert out[0]["direction"] in ("up", "down", "neutral")
        assert 0 <= out[0]["strength"] <= 1.0
