"""
Generates the full "understanding" layer for one headline: summary, why it
matters, short/long-term impact, risks, opportunities, classification,
scope, and a sentiment score. One structured LLM call, validated with
Pydantic before it touches the database.
"""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ValidationError, field_validator

from utils.llm_client import call_llm_json

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "impact_prompt.txt"

ALLOWED_CLASSIFICATIONS = {"Bullish", "Bearish", "Neutral", "Urgent"}
ALLOWED_SCOPES = {
    "Macro", "Micro", "Policy", "Company-specific",
    "Sector-specific", "Global", "India-only",
}


class ImpactResult(BaseModel):
    ai_summary: str
    why_it_matters: str
    short_term_impact: str
    long_term_impact: str
    risks: str
    opportunities: str
    classification: str
    scope: str
    sentiment_score: float

    @field_validator("classification")
    @classmethod
    def check_classification(cls, v):
        return v if v in ALLOWED_CLASSIFICATIONS else "Neutral"

    @field_validator("scope")
    @classmethod
    def check_scope(cls, v):
        return v if v in ALLOWED_SCOPES else "Company-specific"

    @field_validator("sentiment_score")
    @classmethod
    def clamp_sentiment(cls, v):
        return max(-1.0, min(1.0, v))


def analyze_headline(headline: str, source: str) -> Optional[ImpactResult]:
    template = PROMPT_PATH.read_text()
    prompt = template.format(headline=headline, source=source)
    try:
        raw = call_llm_json(prompt)
        return ImpactResult(**raw)
    except (ValidationError, ValueError, KeyError) as exc:
        print(f"[impact_agent] Could not parse impact analysis for '{headline[:60]}...': {exc}")
        return None
