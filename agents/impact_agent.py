"""
Generates the full "understanding" layer for one headline: summary, why it
matters, short/long-term impact, risks, opportunities, classification,
scope, sentiment score, and how it connects to Indian markets (origin +
india_relevance + likely affected Indian sectors). One structured LLM call,
validated with Pydantic before it touches the database.
"""
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, ValidationError, field_validator

from utils.llm_client import call_llm_json
from config.settings import settings

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "impact_prompt.txt"

ALLOWED_CLASSIFICATIONS = {"Bullish", "Bearish", "Neutral", "Urgent"}
ALLOWED_SCOPES = {
    "Macro", "Micro", "Policy", "Company-specific", "Sector-specific",
}
ALLOWED_ORIGINS = {"Domestic", "Global"}


class ImpactResult(BaseModel):
    ai_summary: str = ""
    why_it_matters: str = ""
    short_term_impact: str = ""
    long_term_impact: str = ""
    risks: str = ""
    opportunities: str = ""
    classification: str = "Neutral"
    scope: str = "Company-specific"
    sentiment_score: float = 0.0
    origin: str = "Domestic"
    india_relevance: str = ""
    likely_affected_indian_sectors: List[str] = []

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

    @field_validator("origin")
    @classmethod
    def check_origin(cls, v):
        return v if v in ALLOWED_ORIGINS else "Domestic"

    @field_validator("likely_affected_indian_sectors")
    @classmethod
    def filter_known_sectors(cls, v):
        # Fail-safe: silently drop anything the model invented that isn't
        # actually in our tracked list, rather than rejecting the whole result.
        known = set(settings.TRACKED_INDUSTRIES)
        return [s for s in v if s in known]


def analyze_headline(headline: str, source: str) -> Optional[ImpactResult]:
    template = PROMPT_PATH.read_text()
    prompt = template.format(
        headline=headline,
        source=source,
        known_industries=settings.TRACKED_INDUSTRIES,
    )
    try:
        raw = call_llm_json(prompt)
        return ImpactResult(**raw)
    except (ValidationError, ValueError, KeyError) as exc:
        print(f"[impact_agent] Could not parse impact analysis for '{headline[:60]}...': {exc}")
        return None