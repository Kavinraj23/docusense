from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes.syllabus import router as syllabus_router
from app.routes.auth import router as auth_router  # Add auth router

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