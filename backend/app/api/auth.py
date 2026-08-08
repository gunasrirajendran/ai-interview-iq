from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LogoutRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services.auth_service import AuthService
from app.services.database import get_db
from app.api.deps import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        full_name=user.full_name,
        email=str(user.email),
        password_hash=pwd_context.hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == str(user.email)).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    auth_service = AuthService(db)
    access_token = create_access_token(db_user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = auth_service.create_refresh_token(db_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    record = auth_service.get_valid_refresh_token(payload.refresh_token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token(record.user_id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = auth_service.create_refresh_token(record.user_id)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.revoke_refresh_token(payload.refresh_token)
    return {"status": "logged_out"}


@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset link sent to your email"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name}
