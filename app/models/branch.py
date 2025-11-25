from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(String(512), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="branch")
    infrastructure = relationship("BranchInfrastructure", back_populates="branch", cascade="all, delete-orphan")
    custom_fields = relationship("CustomField", back_populates="branch", cascade="all, delete-orphan")

