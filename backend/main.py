from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, interview, questions, analysis, report, analytics, resume, admin, history, company_modes

app = FastAPI(title="InterviewIQ", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(interview.router, prefix="/interview", tags=["interview"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(report.router, prefix="/report", tags=["report"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(company_modes.router, prefix="/company-modes", tags=["company-modes"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
