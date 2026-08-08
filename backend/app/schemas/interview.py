from pydantic import BaseModel, Field
from typing import Optional, List


class InterviewStartRequest(BaseModel):
    role: str = Field(..., min_length=2)
    difficulty: str = Field(default="medium")
    duration_minutes: int = Field(default=5, ge=1, le=30)


class InterviewStartResponse(BaseModel):
    interview_id: int
    role: str
    difficulty: str
    questions: List[str]
    first_question: str
    first_question_id: int


class AnswerRequest(BaseModel):
    interview_id: int
    question_id: int
    answer: str = Field(..., min_length=1)
    transcript: Optional[str] = None


class AnswerResponse(BaseModel):
    interview_id: int
    question_id: int
    evaluation: dict
    next_question: Optional[dict] = None


class InterviewEndResponse(BaseModel):
    interview_id: int
    status: str
    report: dict
