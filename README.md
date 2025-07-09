# Study Snap

Study Snap is a web app that helps students organize their semester. Upload a syllabus, and the app uses AI to extract important dates and sync them to Google Calendar.

## Live Demo
[https://study-snap-self.vercel.app/](https://study-snap-self.vercel.app/)

## Features

- Upload PDF or DOCX syllabi
- AI extracts class times, exams, and deadlines
- Syncs events to Google Calendar (OAuth)
- Secure login system with JWT auth
- File uploads stored on AWS S3
- Clean, responsive frontend with dark mode

## Tech Stack

**Backend:** FastAPI, PostgreSQL, Google Gemini API, Google Calendar API, AWS S3  
**Frontend:** React (TypeScript), Tailwind CSS, Vite  
**Deployment:** Render (backend), Vercel (frontend), Supabase (PostgreSQL)

## Setup

### Requirements

- Python 3.12+
- Node.js 18+
- PostgreSQL
- AWS S3 bucket
- Google Cloud project

### Backend Setup

```bash
cd backend/app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add environment variables
cp aws_env_example.txt .env
# Fill in your credentials

# Run DB migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install

# Add environment variables
cp env.example .env
# Set your backend API URL

# Start frontend
npm run dev
```
