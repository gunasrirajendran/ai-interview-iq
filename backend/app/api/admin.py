from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.interview import Interview
from app.models.score import Score
from app.services.database import get_db

router = APIRouter()


@router.get("/stats")
def admin_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.email != "admin@example.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access admin stats")
    users = db.query(User).count()
    interviews = db.query(Interview).count()
    scores = db.query(Score).all()
    average_score = round(sum(item.technical_score for item in scores) / len(scores), 1) if scores else 0
    return {
        "total_users": users,
        "total_interviews": interviews,
        "average_score": average_score,
        "daily_active_users": users,
        "top_weak_topics": ["Concurrency", "System Design"],
    }
