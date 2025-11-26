"""
Knowledge base article model
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class KnowledgeArticle(Base):
    """Stores published knowledge-base articles"""
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(String(512), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(120), nullable=True, index=True)
    language = Column(String(8), default="fa", nullable=False)
    tags = Column(JSON, nullable=True)
    is_published = Column(Boolean, default=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    created_by = relationship("User")

    def __repr__(self):
        return f"<KnowledgeArticle(slug='{self.slug}', title='{self.title[:20]}')>"

