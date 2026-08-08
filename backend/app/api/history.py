from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.interview import Interview
from app.models.report import Report
from app.models.score import Score
from app.models.user import User
from app.services.database import get_db

router = APIRouter()


@router.get("/me")
def list_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )
    items = []
    for interview in interviews:
        score = db.query(Score).filter(Score.interview_id == interview.id).order_by(Score.id.desc()).first()
        report = db.query(Report).filter(Report.interview_id == interview.id).first()
        items.append(
            {
                "id": interview.id,
                "interview_type": interview.interview_type,
                "score": interview.score or (score.technical_score if score else 0),
                "created_at": interview.created_at.isoformat() if interview.created_at else None,
                "has_report": report is not None,
            }
        )
    return items
