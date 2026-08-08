# Deployment Guide

## Backend
1. Set environment variables for Gemini, Whisper, and database access.
2. Install Python dependencies: pip install -r backend/requirements.txt.
3. Run: uvicorn main:app --host 0.0.0.0 --port 8000.

## Frontend
1. Install dependencies: npm install.
2. Build: npm run build.
3. Serve via a static host or Vite preview.

## Container
Use docker compose up --build for local deployment.
