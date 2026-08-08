from fastapi import APIRouter, HTTPException
from app.services.gemini_client import GeminiService

router = APIRouter()


@router.post("/generate")
def generate_questions(payload: dict):
    interview_type = payload.get("type", "custom")
    difficulty = payload.get("difficulty", "medium")
    if difficulty not in {"easy", "medium", "hard"}:
        raise HTTPException(status_code=400, detail="Invalid difficulty")
    try:
        service = GeminiService()
        questions = service.generate_questions(interview_type, difficulty)
        return {"questions": questions[:10]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
