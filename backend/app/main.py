from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .routes.syllabus import router as syllabus_router
from .routes.auth import router as auth_router  # Add auth router
from .routes.calendar import router as calendar_router  # Add calendar router

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(syllabus_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])  # Add auth routes
app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])  # Add calendar routes