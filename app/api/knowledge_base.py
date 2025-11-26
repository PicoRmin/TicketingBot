"""
Knowledge base API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.knowledge_base import KnowledgeArticleListResponse, KnowledgeArticleResponse
from app.services.knowledge_base_service import list_articles, get_article_by_slug

router = APIRouter()


@router.get("", response_model=KnowledgeArticleListResponse)
def list_knowledge_articles(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    language: Optional[str] = Query("fa"),
    limit: int = Query(6, ge=1, le=25),
    db: Session = Depends(get_db),
):
    items, total = list_articles(db, category=category, query=q, language=language, limit=limit)
    return KnowledgeArticleListResponse(items=items, total=total)


@router.get("/{slug}", response_model=KnowledgeArticleResponse)
def get_knowledge_article(slug: str, db: Session = Depends(get_db)):
    article = get_article_by_slug(db, slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

