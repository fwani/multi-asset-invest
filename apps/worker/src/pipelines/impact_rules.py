"""Event → asset impact rules: (event_type, impact_type) → direction + strength per asset_type."""

from typing import TypedDict

# Rule entry: which asset_type gets which direction and base strength
ImpactRuleEntry = TypedDict(
    "ImpactRuleEntry",
    {"asset_type": str | None, "direction": str, "base_strength": float},
)

# (event_type, impact_type) -> list of rule entries. None/"*" = any asset type
IMPACT_RULES: dict[tuple[str, str], list[ImpactRuleEntry]] = {
    ("rate_hike", "market"): [
        {"asset_type": "bond", "direction": "down", "base_strength": 0.8},
        {"asset_type": "equity", "direction": "down", "base_strength": 0.5},
        {"asset_type": "stock", "direction": "down", "base_strength": 0.5},
        {"asset_type": "gold", "direction": "up", "base_strength": 0.4},
        {"asset_type": "commodity", "direction": "down", "base_strength": 0.4},
        {"asset_type": "crypto", "direction": "down", "base_strength": 0.6},
        {"asset_type": "fx", "direction": "neutral", "base_strength": 0.3},
    ],
    ("rate_cut", "market"): [
        {"asset_type": "bond", "direction": "up", "base_strength": 0.7},
        {"asset_type": "equity", "direction": "up", "base_strength": 0.5},
        {"asset_type": "stock", "direction": "up", "base_strength": 0.5},
        {"asset_type": "gold", "direction": "up", "base_strength": 0.4},
        {"asset_type": "commodity", "direction": "up", "base_strength": 0.4},
        {"asset_type": "crypto", "direction": "up", "base_strength": 0.5},
        {"asset_type": "fx", "direction": "neutral", "base_strength": 0.3},
    ],
    ("policy_change", "market"): [
        {"asset_type": None, "direction": "neutral", "base_strength": 0.4},
    ],
    ("geopolitical", "market"): [
        {"asset_type": "gold", "direction": "up", "base_strength": 0.6},
        {"asset_type": "commodity", "direction": "up", "base_strength": 0.5},
        {"asset_type": "equity", "direction": "down", "base_strength": 0.5},
        {"asset_type": "stock", "direction": "down", "base_strength": 0.5},
        {"asset_type": "bond", "direction": "up", "base_strength": 0.4},
        {"asset_type": "crypto", "direction": "neutral", "base_strength": 0.3},
        {"asset_type": "fx", "direction": "neutral", "base_strength": 0.3},
    ],
    ("inflation", "market"): [
        {"asset_type": "gold", "direction": "up", "base_strength": 0.6},
        {"asset_type": "commodity", "direction": "up", "base_strength": 0.5},
        {"asset_type": "bond", "direction": "down", "base_strength": 0.6},
        {"asset_type": "equity", "direction": "neutral", "base_strength": 0.4},
        {"asset_type": "stock", "direction": "neutral", "base_strength": 0.4},
        {"asset_type": "crypto", "direction": "neutral", "base_strength": 0.3},
        {"asset_type": "fx", "direction": "neutral", "base_strength": 0.3},
    ],
    ("recession_risk", "market"): [
        {"asset_type": "bond", "direction": "up", "base_strength": 0.5},
        {"asset_type": "gold", "direction": "up", "base_strength": 0.5},
        {"asset_type": "equity", "direction": "down", "base_strength": 0.6},
        {"asset_type": "stock", "direction": "down", "base_strength": 0.6},
        {"asset_type": "commodity", "direction": "down", "base_strength": 0.5},
        {"asset_type": "crypto", "direction": "down", "base_strength": 0.5},
        {"asset_type": "fx", "direction": "neutral", "base_strength": 0.3},
    ],
}

# Fallback when (event_type, impact_type) has no rule: treat as broad market, low strength
DEFAULT_RULES: list[ImpactRuleEntry] = [
    {"asset_type": None, "direction": "neutral", "base_strength": 0.25},
]

# Max number of candidate assets to compute impacts for per event
MAX_CANDIDATE_ASSETS = 100


def get_rules_for_event(
    event_type: str, impact_type: str | None
) -> tuple[list[ImpactRuleEntry], bool]:
    """
    Return (rule entries, used_default) for (event_type, impact_type).
    used_default is True when no specific rule matched and DEFAULT_RULES was returned.
    Normalizes keys (strip, default impact_type to "market").
    """
    et = (event_type or "unknown").strip().lower()
    it = (impact_type or "market").strip().lower()
    key = (et, it)
    if key in IMPACT_RULES:
        return IMPACT_RULES[key], False
    if (et, "market") in IMPACT_RULES:
        return IMPACT_RULES[(et, "market")], False
    return DEFAULT_RULES, True


def _rule_matches_asset(entry: ImpactRuleEntry, asset_type: str) -> bool:
    """True if this rule entry applies to the given asset_type."""
    at = (entry.get("asset_type") or "*").strip().lower()
    if at == "*" or at == "":
        return True
    return asset_type.strip().lower() == at


def compute_impacts(
    event: dict,
    assets: list[dict],
    rules: list[ImpactRuleEntry],
) -> list[dict]:
    """
    Pure function: compute direction and strength per asset from event + rules.
    event: dict with keys event_type, country_id, impact_type, confidence
    assets: list of dicts with keys id, asset_type, country_id
    rules: list of ImpactRuleEntry from get_rules_for_event
    Returns: list of { "asset_id", "direction", "strength" }, strength in [0, 1].
    """
    result = []
    confidence = float(event.get("confidence") or 0.5)
    confidence = max(0.0, min(1.0, confidence))
    event_country_id = event.get("country_id")

    for asset in assets:
        asset_id = asset["id"]
        asset_type = (asset.get("asset_type") or "").strip() or "unknown"
        asset_country_id = asset.get("country_id")

        # Find first matching rule by asset_type
        entry: ImpactRuleEntry | None = None
        for e in rules:
            if _rule_matches_asset(e, asset_type):
                entry = e
                break
        if entry is None:
            entry = {"asset_type": None, "direction": "neutral", "base_strength": 0.25}

        base = float(entry.get("base_strength") or 0.25)
        base = max(0.0, min(1.0, base))
        direction = (entry.get("direction") or "neutral").strip().lower()
        if direction not in ("up", "down", "neutral"):
            direction = "neutral"

        # Country match: same country -> 1.0, else 0.7; if event has no country, treat as 1.0
        if event_country_id is not None and asset_country_id is not None:
            country_factor = 1.0 if event_country_id == asset_country_id else 0.7
        else:
            country_factor = 1.0

        strength = base * confidence * country_factor
        strength = max(0.0, min(1.0, round(strength, 4)))

        result.append({
            "asset_id": asset_id,
            "direction": direction,
            "strength": strength,
        })
    return result
