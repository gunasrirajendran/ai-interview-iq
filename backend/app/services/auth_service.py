import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.orm import Session
from app.models.token import RefreshToken
from app.core.security import create_access_token


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_refresh_token(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        record = RefreshToken(user_id=user_id, token=token)
        self.db.add(record)
        self.db.commit()
        return token

    def revoke_refresh_token(self, token: str) -> None:
        record = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if record:
            record.revoked = 1
            self.db.commit()

    def get_valid_refresh_token(self, token: str) -> RefreshToken | None:
        return self.db.query(RefreshToken).filter(RefreshToken.token == token, RefreshToken.revoked == 0).first()
