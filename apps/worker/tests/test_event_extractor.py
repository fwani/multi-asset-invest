"""Tests for event_extractor: rule-based extraction and LLM fallback."""

import os
from datetime import datetime, timezone
from unittest.mock import patch

from pipelines.event_extractor import extract_events


class TestExtractEventsRules:
    def test_empty_string_returns_empty_list(self):
        assert extract_events("") == []
        assert extract_events("   ") == []

    def test_fed_rate_hike(self):
        text = "The Fed announced a rate hike."
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events(text)
        assert len(result) == 1
        assert result[0]["event_type"] == "rate_hike"
        assert result[0]["country_code"] == "US"
        assert result[0]["impact_type"] == "market"
        assert "actor" in result[0]
        assert result[0].get("confidence", 0) >= 0.6
        assert result[0].get("metadata_", {}).get("extraction_source") == "rules"

    def test_ecb_rate_cut(self):
        text = "ECB cuts interest rates."
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events(text)
        assert len(result) == 1
        assert result[0]["event_type"] == "rate_cut"
        assert result[0]["country_code"] == "EU"
        assert result[0]["impact_type"] == "market"

    def test_inflation(self):
        text = "Inflation rises to 5%."
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events(text)
        assert len(result) == 1
        assert result[0]["event_type"] == "inflation"
        assert result[0]["impact_type"] == "market"

    def test_policy_change_fallback(self):
        text = "Markets were mixed on Tuesday."
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events(text)
        assert len(result) == 1
        assert result[0]["event_type"] == "policy_change"
        assert 0.4 <= (result[0].get("confidence") or 0) <= 0.6
        # Uncertain path: LLM was attempted but returned None (mock)
        assert result[0].get("metadata_", {}).get("llm_attempted") is True

    def test_occurred_at_passed_through(self):
        ts = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events("Rate hike by the Fed.", occurred_at=ts)
        assert len(result) == 1
        assert result[0]["occurred_at"] == ts

    def test_source_summary_length(self):
        long_text = "x" * 600
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events(long_text)
        assert len(result) == 1
        summary = result[0].get("source_summary") or ""
        assert len(summary) <= 501
        assert "…" in summary or len(long_text.strip()) <= 500

    def test_return_keys(self):
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events("Fed raises rates.")
        assert len(result) == 1
        keys = set(result[0].keys())
        required = {
            "event_type", "country_id", "country_code", "actor", "impact_type",
            "occurred_at", "source_summary", "confidence", "metadata_",
        }
        assert keys >= required
        assert result[0]["country_id"] is None
        assert result[0]["metadata_"].get("extraction_source") == "rules"


class TestExtractEventsLLMFallback:
    def test_uncertain_input_triggers_llm_and_uses_result(self):
        # Text that yields policy_change / uncertain by rules
        text = "Some development in the economy."
        llm_return = {
            "event_type": "inflation",
            "country_code": "US",
            "actor": "Fed",
            "confidence": 0.85,
        }
        with patch("pipelines.event_extractor._call_llm", return_value=(llm_return, "gpt-4o-mini")) as m:
            result = extract_events(text)
        assert m.call_count == 1
        assert len(result) == 1
        assert result[0]["event_type"] == "inflation"
        assert result[0]["country_code"] == "US"
        assert result[0]["actor"] == "Fed"
        assert result[0]["confidence"] == 0.85
        assert result[0]["metadata_"].get("extraction_source") == "llm"
        assert result[0]["metadata_"].get("llm_model") == "gpt-4o-mini"

    def test_no_api_key_skips_llm(self):
        text = "Some development in the economy."
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            result = extract_events(text)
        assert len(result) == 1
        assert result[0]["event_type"] == "policy_change"

    def test_openai_not_called_when_api_key_missing(self):
        text = "Some development in the economy."
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            with patch("openai.OpenAI") as mock_client:
                result = extract_events(text)
        mock_client.assert_not_called()
        assert result[0]["event_type"] == "policy_change"

    def test_llm_returns_none_keeps_rule_result(self):
        text = "Some development in the economy."
        with patch("pipelines.event_extractor._call_llm", return_value=(None, None)):
            result = extract_events(text)
        assert len(result) == 1
        assert result[0]["event_type"] == "policy_change"
        assert result[0]["metadata_"].get("extraction_source") == "rules"
        assert result[0]["metadata_"].get("llm_attempted") is True
