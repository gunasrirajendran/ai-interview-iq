from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    technical_score = Column(Integer, default=0)
    communication_score = Column(Integer, default=0)
    confidence_score = Column(Integer, default=0)
    eye_contact_score = Column(Integer, default=0)
