"""
Tags a news headline with the companies/industries it's actually about,
using a constrained-JSON LLM prompt. Output is validated with Pydantic
before it's ever written to the database.
"""
from pathlib import Path
from typing import List
from pydantic import BaseModel, ValidationError

from utils.llm_client import call_llm_json
from config.settings import settings

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "tagging_prompt.txt"


class TagResult(BaseModel):
    companies: List[str] = []
    industries: List[str] = []


def tag_headline(headline: str) -> TagResult:
    template = PROMPT_PATH.read_text()
    prompt = template.format(
        headline=headline,
        known_companies=settings.TRACKED_TICKERS,
        known_industries=settings.TRACKED_INDUSTRIES,
    )
    try:
        raw = call_llm_json(prompt)
        return TagResult(**raw)
    except (ValidationError, ValueError, KeyError) as exc:
        # Fail safe: an unparseable/invalid response just means "no tags found"
        # rather than crashing the whole daily pipeline.
        print(f"[tagging_agent] Could not parse tags for '{headline[:60]}...': {exc}")
        return TagResult()
