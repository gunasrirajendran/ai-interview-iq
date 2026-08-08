from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User
from app.services.database import get_db
from app.services.interview_service import InterviewService

router = APIRouter()


@router.get("/{interview_id}")
def get_report(interview_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = InterviewService(db)
        return service.get_report(interview_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
