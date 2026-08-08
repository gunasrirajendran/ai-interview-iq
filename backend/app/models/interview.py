from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_type = Column(String(100), nullable=False)
    score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
