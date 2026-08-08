import os
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.services.database import get_db
from app.services.resume_service import ResumeService

router = APIRouter()


@router.post("/upload")
def upload_resume(file: UploadFile = File(...), user_id: int = 1, db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF resumes are supported')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        service = ResumeService()
        data = service.extract_resume(tmp_path)
        resume = Resume(
            user_id=user_id,
            file_name=file.filename,
            extracted_text=data['text'],
            detected_skills=','.join(data['skills']),
            detected_projects=','.join(data['projects']),
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return {"id": resume.id, "skills": data['skills'], "projects": data['projects']}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
