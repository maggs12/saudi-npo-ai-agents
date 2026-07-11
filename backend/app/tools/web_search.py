from typing import Any

from app.core.config import settings


def web_search(query: str, max_results: int | None = None) -> list[dict[str, str]]:
    """Search the web using DuckDuckGo and return a list of results."""
    max_results = max_results or settings.web_search_max_results
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = ddgs.text(
                keywords=query,
                region="sa-ar",
                max_results=max_results,
            )
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", ""),
                }
                for r in results
            ]
    except Exception as exc:
        return [
            {
                "title": "Search error",
                "url": "",
                "body": f"Could not perform web search: {exc}",
            }
        ]
