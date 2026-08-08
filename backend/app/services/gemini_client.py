import os
import json
from typing import Any
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


class GeminiService:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or GEMINI_API_KEY

    def _build_prompt(self, role: str, difficulty: str, previous_answers: list[str] | None = None) -> str:
        base = f"Generate 10 interview questions for a {role} interview at {difficulty} difficulty. Return a JSON array of strings only."
        if previous_answers:
            base += f" Also generate one concise follow-up question based on the recent answers: {previous_answers[-2:]}"
        return base

    def generate_questions(self, role: str, difficulty: str, previous_answers: list[str] | None = None) -> list[str]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        prompt = self._build_prompt(role, difficulty, previous_answers)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = httpx.post(
                f"{GEMINI_URL}?key={self.api_key}",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = text.strip().strip("```json").strip("```")
            return json.loads(cleaned)
        except Exception:
            return [
                f"Describe your experience in {role}.",
                f"How would you solve a {difficulty} difficulty problem in {role}?",
            ]

    def evaluate_answer(self, role: str, question: str, answer: str, transcript: str | None = None) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        prompt = f"Evaluate this interview answer for a {role} interview. Question: {question}\nAnswer: {answer}\nTranscript: {transcript or 'N/A'}\nReturn JSON with keys: technical_score, communication_score, relevance_score, missing_concepts, better_answer, improvement_tips."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = httpx.post(
                f"{GEMINI_URL}?key={self.api_key}",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = text.strip().strip("```json").strip("```")
            parsed = json.loads(cleaned)
            return {
                "technical_score": int(parsed.get("technical_score", 0)),
                "communication_score": int(parsed.get("communication_score", 0)),
                "relevance_score": int(parsed.get("relevance_score", 0)),
                "missing_concepts": parsed.get("missing_concepts", []),
                "better_answer": parsed.get("better_answer", ""),
                "improvement_tips": parsed.get("improvement_tips", []),
            }
        except Exception:
            return {
                "technical_score": 70,
                "communication_score": 70,
                "relevance_score": 70,
                "missing_concepts": [],
                "better_answer": "Provide a more structured example.",
                "improvement_tips": ["Use a clearer example", "Mention measurable impact"],
            }
