from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from app.models.base import Base
from app.models.user import User
from app.models.interview import Interview
from app.models.question import Question
from app.models.response import Response
from app.models.score import Score
from app.models.report import Report
from app.models.analytics import AnalyticsEvent
from app.models.token import RefreshToken
from app.models.resume import Resume


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
