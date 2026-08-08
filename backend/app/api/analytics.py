import json
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.analytics import AnalyticsEvent
from app.services.database import get_db
from app.services.media_service import MediaAnalysisService

router = APIRouter()


@router.post("/event")
def create_event(payload: dict, db: Session = Depends(get_db)):
    event = AnalyticsEvent(
        interview_id=int(payload.get("interview_id", 0)),
        event_type=str(payload.get("event_type", "event")),
        timestamp=float(payload.get("timestamp", time.time())),
        details=json.dumps(payload.get("details", {})) if isinstance(payload.get("details"), dict) else str(payload.get("details", "")),
    )
    db.add(event)
    db.commit()
    return {"status": "ok"}


@router.post("/live/{interview_id}")
def create_live_snapshot(interview_id: int, payload: dict, db: Session = Depends(get_db)):
    image_data = payload.get("image") or payload.get("frame") or payload.get("image_data")
    if not image_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image payload is required")
    service = MediaAnalysisService()
    snapshot = service.analyze_image_data(image_data)
    snapshot["interview_id"] = interview_id
    event = AnalyticsEvent(
        interview_id=interview_id,
        event_type="live_snapshot",
        timestamp=float(snapshot.get("timestamp", time.time())),
        details=json.dumps(snapshot),
    )
    db.add(event)
    db.commit()
    return snapshot


@router.get("/events/{interview_id}")
def list_events(interview_id: int, db: Session = Depends(get_db)):
    events = db.query(AnalyticsEvent).filter(AnalyticsEvent.interview_id == interview_id).all()
    return [{"id": e.id, "event_type": e.event_type, "timestamp": e.timestamp, "details": e.details} for e in events]


@router.get("/live/{interview_id}")
def get_live_snapshot(interview_id: int, db: Session = Depends(get_db)):
    event = (
        db.query(AnalyticsEvent)
        .filter(AnalyticsEvent.interview_id == interview_id, AnalyticsEvent.event_type == "live_snapshot")
        .order_by(AnalyticsEvent.created_at.desc())
        .first()
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No live analytics found")
    return json.loads(event.details) if event.details else {}


@router.get("/history/{interview_id}")
def get_history(interview_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(AnalyticsEvent)
        .filter(AnalyticsEvent.interview_id == interview_id, AnalyticsEvent.event_type == "live_snapshot")
        .order_by(AnalyticsEvent.created_at.desc())
        .all()
    )
    return [json.loads(event.details) if event.details else {} for event in events]
