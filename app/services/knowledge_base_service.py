"""
Service helpers for knowledge base articles
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import KnowledgeArticle
from app.schemas.knowledge_base import KnowledgeArticleBase


def list_articles(
    db: Session,
    category: Optional[str] = None,
    query: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 10,
) -> Tuple[List[KnowledgeArticle], int]:
    q = db.query(KnowledgeArticle).filter(KnowledgeArticle.is_published.is_(True))
    if category:
        q = q.filter(KnowledgeArticle.category == category)
    if language:
        q = q.filter(KnowledgeArticle.language == language)
    if query:
        like = f"%{query}%"
        q = q.filter((KnowledgeArticle.title.ilike(like)) | (KnowledgeArticle.summary.ilike(like)))
    total = q.count()
    items = (
        q.order_by(KnowledgeArticle.updated_at.desc())
        .limit(limit)
        .all()
    )
    return items, total


def get_article_by_slug(db: Session, slug: str) -> Optional[KnowledgeArticle]:
    return (
        db.query(KnowledgeArticle)
        .filter(KnowledgeArticle.slug == slug, KnowledgeArticle.is_published.is_(True))
        .first()
    )


def create_article(
    db: Session,
    data: KnowledgeArticleBase,
    created_by_id: Optional[int] = None,
) -> KnowledgeArticle:
    article = KnowledgeArticle(
        slug=data.slug,
        title=data.title,
        summary=data.summary,
        content=data.content,
        category=data.category,
        language=data.language or "fa",
        tags=data.tags,
        is_published=data.is_published,
        created_by_id=created_by_id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

