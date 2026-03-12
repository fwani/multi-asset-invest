"""LLM prompt templates for pipelines."""

from pipelines.prompts.event_extractor import EVENT_EXTRACTOR_SYSTEM_PROMPT
from pipelines.prompts.impact_calculator import IMPACT_CALCULATOR_SYSTEM_PROMPT

__all__ = ["EVENT_EXTRACTOR_SYSTEM_PROMPT", "IMPACT_CALCULATOR_SYSTEM_PROMPT"]
