from pipelines.news.dedup import _similar


def test_similar_identical_strings():
    assert _similar("Reliance profits jump 20%", "Reliance profits jump 20%") == 1.0


def test_similar_different_strings():
    score = _similar("Reliance profits jump 20%", "Tesla unveils new factory")
    assert score < 0.5


def test_similar_near_duplicate_headlines():
    a = "RBI keeps repo rate unchanged at 6.5%"
    b = "RBI keeps the repo rate unchanged at 6.5 percent"
    assert _similar(a, b) > 0.7
