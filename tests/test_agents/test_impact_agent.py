from agents.impact_agent import ImpactResult


def test_impact_result_clamps_sentiment():
    result = ImpactResult(
        ai_summary="test", why_it_matters="test", short_term_impact="test",
        long_term_impact="test", risks="test", opportunities="test",
        classification="Bullish", scope="Macro", sentiment_score=5.0,
    )
    assert result.sentiment_score == 1.0


def test_impact_result_rejects_bad_classification():
    result = ImpactResult(
        ai_summary="test", why_it_matters="test", short_term_impact="test",
        long_term_impact="test", risks="test", opportunities="test",
        classification="SuperBullish", scope="Macro", sentiment_score=0.5,
    )
    assert result.classification == "Neutral"
