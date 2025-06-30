from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from sqlalchemy import text
from db.session import engine

# Use absolute imports for production
from routes.syllabus import router as syllabus_router
from routes.auth import router as auth_router
from routes.calendar import router as calendar_router

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Study Snap API",
    description="AI-Powered Academic Organizer API",
    version="1.0.0"
)

# Get CORS origins from environment variables
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Use the variable instead of hardcoded value
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for production monitoring."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "study-snap-api",
        "database": db_status,
        "timestamp": "2024-01-01T00:00:00Z"  # You can add proper timestamp here
    }

# Include routers
app.include_router(syllabus_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])  # Add auth routes
app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])  # Add calendar routes