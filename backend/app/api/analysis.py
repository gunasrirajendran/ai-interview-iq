from fastapi import APIRouter

router = APIRouter()


@router.post("/speech")
def analyze_speech(payload: dict):
    text = payload.get("text", "")
    filler_words = sum(1 for word in text.lower().split() if word in {"um", "uh", "like"})
    return {
        "transcript": text,
        "filler_words": filler_words,
        "speaking_speed": 140,
        "pause_analysis": "Balanced pacing",
    }


@router.post("/face")
def analyze_face(payload: dict):
    return {
        "eye_contact": 82,
        "head_movement": 12,
        "looking_away": 4,
        "smile_frequency": 3,
    }
