# InterviewIQ – AI Interview Assessment Platform

InterviewIQ is a production-ready AI interview platform with live interview analytics, resume parsing, company-specific interview modes, reporting, and admin insights.

## Features
- AI question generation with Gemini
- Speech transcription with Whisper
- Webcam-based analytics with MediaPipe and OpenCV
- Resume upload and parsing
- Company-based interview modes
- Interview history and replay support
- Final report generation and PDF export flow
- Admin dashboard metrics
- JWT-based auth and input validation

## Architecture
- Frontend: React + Vite + Tailwind
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL / SQLite for local development

## Backend setup
1. cd backend
2. python -m venv .venv
3. .venv\\Scripts\\activate
4. pip install -r requirements.txt
5. uvicorn main:app --reload

## Frontend setup
1. cd frontend
2. npm install
3. npm run dev

## Environment variables
Set the following in the backend environment:
- GEMINI_API_KEY
- OPENAI_API_KEY
- DATABASE_URL

## API docs
- Swagger UI: /docs
- ReDoc: /redoc

## Folder tree
- backend/app/api
- backend/app/models
- backend/app/services
- backend/app/schemas
- frontend/src/pages
- frontend/src/components
- frontend/src/lib
