"""
Pydantic schemas for knowledge base
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class KnowledgeArticleBase(BaseModel):
    slug: str
    title: str
    summary: Optional[str]
    content: str
    category: Optional[str]
    language: str = "fa"
    tags: List[str] = []
    is_published: bool = True


class KnowledgeArticleResponse(KnowledgeArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class KnowledgeArticleListResponse(BaseModel):
    items: List[KnowledgeArticleResponse]
    total: int

