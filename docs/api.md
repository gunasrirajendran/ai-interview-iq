# API Documentation

## Authentication
- POST /auth/register
- POST /auth/login
- POST /auth/forgot-password

## Interview
- POST /interview/start
- GET /interview/questions
- POST /interview/answer
- POST /interview/audio
- POST /interview/end

## Analysis
- POST /analytics/event
- GET /analytics/events/{interview_id}

## Resume
- POST /resume/upload

## Reporting
- GET /report/{interview_id}

## Admin
- GET /admin/stats
