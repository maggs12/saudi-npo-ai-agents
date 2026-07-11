from typing import Any

from sqlmodel import Session, select

from app.core.providers import embedding_provider
from app.models import Regulation
from app.tools.web_search import web_search


def add_regulation(session: Session, title: str, content: str, source_url: str) -> Regulation:
    embedding = embedding_provider.embed([content])[0] if content else None
    regulation = Regulation(
        title=title,
        content=content,
        source_url=source_url,
        embedding=embedding,
    )
    session.add(regulation)
    session.commit()
    session.refresh(regulation)
    return regulation


def search_regulations(session: Session, query: str, top_k: int = 3) -> list[Regulation]:
    """Search stored regulations using vector similarity."""
    try:
        embedding = embedding_provider.embed([query])[0]
    except Exception:
        embedding = [0.0] * 384

    results = session.exec(
        select(Regulation)
        .order_by(Regulation.embedding.cosine_distance(embedding))
        .limit(top_k)
    ).all()
    return list(results)


def add_regulations_from_web_search(session: Session, query: str) -> list[Regulation]:
    """Search the web for regulations, store them, and return the stored records."""
    results = []
    for item in web_search(query, max_results=5):
        existing = session.exec(
            select(Regulation).where(Regulation.source_url == item["url"])
        ).first()
        if not existing:
            regulation = add_regulation(
                session,
                title=item.get("title", ""),
                content=item.get("body", ""),
                source_url=item.get("url", ""),
            )
            results.append(regulation)
    return results


def search_regulations_with_fallback(session: Session, query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Search stored regulations; if empty, fetch from web first."""
    stored = search_regulations(session, query, top_k=top_k)
    if not stored:
        stored = add_regulations_from_web_search(session, query)
    return [
        {
            "title": r.title,
            "content": r.content,
            "source_url": r.source_url,
        }
        for r in stored
    ]
