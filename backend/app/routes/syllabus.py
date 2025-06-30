"""
Syllabus routes for handling syllabus upload and management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import shutil
import os
import uuid
from datetime import datetime
from db.session import SessionLocal
from db.models.syllabus import Syllabus
from services.gemini import extract_syllabus_info
from services.extractor import extract_text
from services.s3_service import s3_service
from pydantic import BaseModel
from services.security import get_current_user  # <-- Import the auth dependency
from db.deps import get_db
from db.models.user import User

class ColorUpdate(BaseModel):
    accent_color: str

class ImportantDates(BaseModel):
    first_class: str
    last_class: str
    midterms: List[str]
    final_exam: str

class SyllabusUpdate(BaseModel):
    important_dates: ImportantDates

class SyllabusResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    upload_time: datetime
    course_code: Optional[str]
    course_name: Optional[str]
    instructor_name: Optional[str]
    instructor_email: Optional[str]
    semester: Optional[str]
    year: Optional[str]
    description: Optional[str]
    accent_color: Optional[str]
    meeting_days: Optional[str]
    meeting_time: Optional[str]
    meeting_location: Optional[str]
    first_class: Optional[str]
    last_class: Optional[str]
    midterm_dates: Optional[str]
    final_exam_date: Optional[str]
    grading_policy: Optional[str]
    schedule_summary: Optional[str]

    class Config:
        from_attributes = True

router = APIRouter()

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

ACCEPTED_EXTENSIONS = {".pdf", ".docx" }

def is_allowed_file(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ACCEPTED_EXTENSIONS)

@router.post("/upload", response_model=SyllabusResponse)
async def upload_syllabus(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a syllabus file."""
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and DOC files are allowed")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to S3
        file_name = f"syllabi/{current_user.id}/{uuid.uuid4()}_{file.filename}"
        file_url = s3_service.upload_file(file_content, file_name, file.content_type)
        
        # Extract text from file
        text_content = extract_text(file_content, file.filename)
        
        # Extract syllabus information using Gemini
        syllabus_info = extract_syllabus_info(text_content)
        
        # Create syllabus record
        syllabus = Syllabus(
            user_id=current_user.id,
            filename=file.filename,
            content_type=file.content_type,
            course_name=syllabus_info.get('title', file.filename),
            course_code=syllabus_info.get('course_code', ''),
            instructor_name=syllabus_info.get('instructor', {}).get('name', ''),
            instructor_email=syllabus_info.get('instructor', {}).get('email', ''),
            semester=syllabus_info.get('term', {}).get('semester', ''),
            year=syllabus_info.get('term', {}).get('year', ''),
            description=syllabus_info.get('description', ''),
            meeting_days=syllabus_info.get('meeting_info', {}).get('days', ''),
            meeting_time=syllabus_info.get('meeting_info', {}).get('time', ''),
            meeting_location=syllabus_info.get('meeting_info', {}).get('location', ''),
            first_class=syllabus_info.get('important_dates', {}).get('first_class', ''),
            last_class=syllabus_info.get('important_dates', {}).get('last_class', ''),
            midterm_dates=json.dumps(syllabus_info.get('important_dates', {}).get('midterms', [])),
            final_exam_date=syllabus_info.get('important_dates', {}).get('final_exam', ''),
            grading_policy=json.dumps(syllabus_info.get('grading_policy', {})),
            schedule_summary=syllabus_info.get('schedule_summary', '')
        )
        
        db.add(syllabus)
        db.commit()
        db.refresh(syllabus)
        
        return syllabus
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process syllabus: {str(e)}")

@router.get("/", response_model=List[SyllabusResponse])
async def get_syllabi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all syllabi for the current user."""
    syllabi = db.query(Syllabus).filter(Syllabus.user_id == current_user.id).all()
    return syllabi

@router.get("/{syllabus_id}", response_model=SyllabusResponse)
async def get_syllabus(
    syllabus_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific syllabus by ID."""
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.user_id == current_user.id
    ).first()
    
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    return syllabus

@router.delete("/{syllabus_id}")
async def delete_syllabus(
    syllabus_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a syllabus."""
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.user_id == current_user.id
    ).first()
    
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Delete from S3 if file exists
    # Note: We don't store file_url in the database anymore, so we can't delete from S3
    # The file will remain in S3 for now
    pass
    
    db.delete(syllabus)
    db.commit()
    
    return {"message": "Syllabus deleted successfully"}

@router.patch("/syllabi/{syllabus_id}/color")
def update_syllabus_color(
    syllabus_id: int,
    color_update: ColorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- Require authentication
):
    # Only allow users to update their own syllabi
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.user_id == current_user.id
    ).first()
    
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    syllabus.accent_color = color_update.accent_color
    db.commit()
    return {"status": "success"}

@router.patch("/syllabi/{syllabus_id}")
def update_syllabus_details(
    syllabus_id: int,
    syllabus_update: SyllabusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- Require authentication
):
    # Only allow users to update their own syllabi
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.user_id == current_user.id
    ).first()
    
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Update the important dates
    if syllabus_update.important_dates:
        syllabus.first_class = syllabus_update.important_dates.first_class
        syllabus.last_class = syllabus_update.important_dates.last_class
        syllabus.midterm_dates = json.dumps(syllabus_update.important_dates.midterms)
        syllabus.final_exam_date = syllabus_update.important_dates.final_exam
    
    db.commit()
    db.refresh(syllabus)
    
    return {"message": "Syllabus updated successfully"}

