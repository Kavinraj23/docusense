# 🎓 Study Snap — AI-Powered Academic Organizer

**Study Snap** is a full-stack platform that uses AI to extract and organize information from college syllabi, automatically syncing important dates to Google Calendar.

🌐 **Live Demo**: [https://study-snap-self.vercel.app/](https://study-snap-self.vercel.app/)

> ⚠️ **Note**: Login/Signup functionality is currently not working and will be available soon.

## ✨ Features

- **AI Syllabus Processing**: Extract course info, dates, and meeting details from PDF/DOCX files
- **Google Calendar Sync**: OAuth integration to automatically create calendar events
- **Smart Date Management**: Track classes, midterms, and final exams with validation
- **Secure Authentication**: JWT-based user authentication with password hashing
- **Cloud Storage**: AWS S3 integration for file management
- **Modern UI**: Responsive design with dark/light mode support

## 🏗️ Architecture

### Backend (FastAPI + Python 3.12.5)
- FastAPI with async support
- PostgreSQL with SQLAlchemy ORM
- Google Gemini API for AI text extraction
- Google Calendar API integration
- AWS S3 for file storage

### Frontend (React + TypeScript)
- React 18 with TypeScript
- Vite for fast builds
- Tailwind CSS for styling
- Axios for API communication

## 🚀 Deployment

- **Backend**: Render (Python 3.12.5)
- **Frontend**: Vercel
- **Database**: Supabase PostgreSQL
- **Storage**: AWS S3

### Environment Variables

#### Backend
```env
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-secret-key
GOOGLE_GEMINI_API_KEY=your-gemini-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
CORS_ORIGINS=https://your-frontend-domain.com
```

#### Frontend
```env
VITE_API_BASE_URL=https://your-backend-domain.com
```

## 🛠️ Local Development

### Prerequisites
- Python 3.12.5+
- Node.js 18+
- PostgreSQL database
- AWS S3 bucket
- Google Cloud Project

### Backend Setup
```bash
cd backend/app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp aws_env_example.txt .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# Set environment
cp env.example .env
# Edit .env with backend URL

# Start dev server
npm run dev
```

## 📁 Project Structure

```
study-snap/
├── backend/app/
│   ├── alembic/           # Database migrations
│   ├── db/                # Database models
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   └── main.py           # FastAPI app
├── frontend/src/
│   ├── components/       # React components
│   ├── contexts/         # React contexts
│   ├── features/         # Feature modules
│   ├── pages/           # Page components
│   └── services/        # API services
└── README.md
```

## 🔧 Key API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /upload` - Upload and process syllabus
- `GET /` - Get user's syllabi
- `GET /calendar/auth/google` - Initiate Google OAuth
- `POST /calendar/sync-syllabus` - Sync syllabus to calendar

---

