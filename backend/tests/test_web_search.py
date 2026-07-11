from app.tools.web_search import web_search


def test_web_search_returns_results():
    results = web_search("NCNP non-profit Saudi governance", max_results=3)
    assert isinstance(results, list)
    assert len(results) <= 3
    if len(results) > 0:
        assert "title" in results[0]
        assert "url" in results[0]
