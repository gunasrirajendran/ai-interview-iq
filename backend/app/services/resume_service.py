import os
import re
from typing import Any
from pypdf import PdfReader


class ResumeService:
    def extract_resume(self, file_path: str) -> dict[str, Any]:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        skills = self._extract_skills(text)
        projects = self._extract_projects(text)
        return {
            "text": text,
            "skills": skills,
            "projects": projects,
        }

    def _extract_skills(self, text: str) -> list[str]:
        skill_keywords = ["python", "java", "sql", "fastapi", "react", "docker", "aws", "kubernetes", "machine learning", "backend", "microservices"]
        found = [skill for skill in skill_keywords if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)]
        return found

    def _extract_projects(self, text: str) -> list[str]:
        sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
        return [s.strip() for s in sentences if len(s.strip()) > 20][:5]
