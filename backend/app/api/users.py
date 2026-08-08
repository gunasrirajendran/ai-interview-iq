from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user as get_authenticated_user
from app.models.user import User
from app.schemas.user import UserOut
from app.services.database import get_db

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_current_user(current_user: User = Depends(get_authenticated_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
