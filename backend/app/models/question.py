from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    difficulty = Column(String(50), default="medium")
