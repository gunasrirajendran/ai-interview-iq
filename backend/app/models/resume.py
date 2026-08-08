from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=True)
    detected_skills = Column(Text, nullable=True)
    detected_projects = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
