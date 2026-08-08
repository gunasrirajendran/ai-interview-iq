import logging
from typing import Any
from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.models.question import Question
from app.models.response import Response
from app.models.score import Score
from app.models.report import Report
from app.services.gemini_client import GeminiService
from app.services.whisper_client import WhisperService

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.gemini = GeminiService()
        self.whisper = WhisperService()

    def create_interview(self, role: str, difficulty: str, duration_minutes: int, user_id: int = 1) -> dict[str, Any]:
        interview = Interview(user_id=user_id, interview_type=role, score=0)
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)

        try:
            questions = self.gemini.generate_questions(role, difficulty)
        except Exception as exc:
            logger.exception("Gemini question generation failed")
            questions = [f"Describe your experience in {role}.", f"How would you solve a {difficulty} difficulty problem in {role}?"]

        saved_questions = []
        for idx, prompt in enumerate(questions[:10], start=1):
            question = Question(interview_id=interview.id, prompt=prompt, difficulty=difficulty)
            self.db.add(question)
            self.db.commit()
            self.db.refresh(question)
            saved_questions.append({"id": question.id, "text": question.prompt})

        return {
            "interview_id": interview.id,
            "role": role,
            "difficulty": difficulty,
            "questions": [q["text"] for q in saved_questions],
            "first_question": saved_questions[0]["text"],
            "first_question_id": saved_questions[0]["id"],
        }

    def submit_answer(self, interview_id: int, question_id: int, answer: str, transcript: str | None = None) -> dict[str, Any]:
        if not answer or not answer.strip():
            raise ValueError("Answer cannot be empty")
        response_record = Response(question_id=question_id, answer_text=answer, transcript_text=transcript)
        self.db.add(response_record)
        self.db.commit()
        self.db.refresh(response_record)

        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
        role = interview.interview_type if interview else "custom"
        evaluation = self.gemini.evaluate_answer(role, question.prompt, answer, transcript)
        score_record = Score(
            interview_id=interview_id,
            technical_score=evaluation["technical_score"],
            communication_score=evaluation["communication_score"],
            confidence_score=evaluation["relevance_score"],
            eye_contact_score=0,
        )
        self.db.add(score_record)
        self.db.commit()

        next_question = self.db.query(Question).filter(Question.id > question_id).order_by(Question.id).first()
        if next_question:
            return {
                "interview_id": interview_id,
                "question_id": question_id,
                "evaluation": evaluation,
                "next_question": {"id": next_question.id, "text": next_question.prompt},
            }
        return {
            "interview_id": interview_id,
            "question_id": question_id,
            "evaluation": evaluation,
            "next_question": None,
        }

    def transcribe_audio(self, audio_file) -> str:
        return self.whisper.transcribe_audio(audio_file)

    def end_interview(self, interview_id: int) -> dict[str, Any]:
        latest_score = self.db.query(Score).filter(Score.interview_id == interview_id).order_by(Score.id.desc()).first()
        if latest_score is None:
            raise ValueError("No evaluation found for this interview")
        report_text = (
            f"Technical: {latest_score.technical_score}; Communication: {latest_score.communication_score}; "
            f"Confidence: {latest_score.confidence_score}; Eye Contact: {latest_score.eye_contact_score}"
        )
        report = Report(interview_id=interview_id, report_text=report_text)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return {"interview_id": interview_id, "status": "completed", "report": {"report_id": report.id, "summary": report_text}}

    def get_report(self, interview_id: int) -> dict[str, Any]:
        report = self.db.query(Report).filter(Report.interview_id == interview_id).first()
        if report is None:
            raise ValueError("Report not found")
        scores = self.db.query(Score).filter(Score.interview_id == interview_id).all()
        return {
            "interview_id": interview_id,
            "report_id": report.id,
            "summary": report.report_text,
            "scores": [
                {
                    "technical_score": item.technical_score,
                    "communication_score": item.communication_score,
                    "confidence_score": item.confidence_score,
                    "eye_contact_score": item.eye_contact_score,
                }
                for item in scores
            ],
        }
