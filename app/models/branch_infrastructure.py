"""
Branch Infrastructure model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BranchInfrastructure(Base):
    """Branch Infrastructure model for storing IPs, servers, equipment, services"""
    __tablename__ = "branch_infrastructure"
    
    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    infrastructure_type = Column(String(50), nullable=False, index=True)  # ip, server, equipment, service
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)  # For IPs and servers
    hostname = Column(String(255), nullable=True)  # For servers
    model = Column(String(255), nullable=True)  # For equipment
    serial_number = Column(String(255), nullable=True)  # For equipment
    service_type = Column(String(100), nullable=True)  # For services
    service_url = Column(String(512), nullable=True)  # For services
    status = Column(String(50), default="active", nullable=False)  # active, inactive, maintenance
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    branch = relationship("Branch", back_populates="infrastructure")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    def __repr__(self):
        return f"<BranchInfrastructure(id={self.id}, branch_id={self.branch_id}, type={self.infrastructure_type}, name='{self.name}')>"

