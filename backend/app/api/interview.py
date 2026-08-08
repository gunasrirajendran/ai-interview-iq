import logging
from typing import Any
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import AnswerRequest, AnswerResponse, InterviewEndResponse, InterviewStartRequest, InterviewStartResponse
from app.services.database import get_db
from app.services.interview_service import InterviewService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/types")
def interview_types() -> list[dict[str, str]]:
    return [
        {"slug": "hr", "name": "HR"},
        {"slug": "java", "name": "Java"},
        {"slug": "python", "name": "Python"},
        {"slug": "sql", "name": "SQL"},
        {"slug": "dsa", "name": "DSA"},
        {"slug": "custom", "name": "Custom Interview"},
    ]


@router.post("/start", response_model=InterviewStartResponse)
def start_interview(
    payload: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewStartResponse:
    try:
        service = InterviewService(db)
        result = service.create_interview(payload.role, payload.difficulty, payload.duration_minutes, user_id=current_user.id)
        return InterviewStartResponse(**result)

    except Exception as exc:
        logger.exception("Failed to start interview")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/questions")
def get_questions(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    from app.models.question import Question
    questions = db.query(Question).all()
    return [{"id": q.id, "text": q.prompt, "difficulty": q.difficulty} for q in questions]


@router.post("/answer", response_model=AnswerResponse)
def submit_answer(payload: AnswerRequest, db: Session = Depends(get_db)) -> AnswerResponse:
    try:
        service = InterviewService(db)
        result = service.submit_answer(payload.interview_id, payload.question_id, payload.answer, payload.transcript)
        return AnswerResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to evaluate answer")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/audio", response_model=dict)
def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        service = InterviewService(db)
        transcript = service.transcribe_audio(file.file)
        return {"transcript": transcript}
    except Exception as exc:
        logger.exception("Audio transcription failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/end", response_model=InterviewEndResponse)
def end_interview(interview_id: int, db: Session = Depends(get_db)) -> InterviewEndResponse:
    try:
        service = InterviewService(db)
        result = service.end_interview(interview_id)
        return InterviewEndResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to complete interview")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
