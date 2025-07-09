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

class UploadResponse(BaseModel):
    filename: str
    metadata: dict

class SyllabusResponse(BaseModel):
    id: int
    filename: str
    course_code: str
    course_name: str
    instructor: dict
    term: dict
    description: str
    meeting_info: dict
    important_dates: dict
    grading_policy: dict
    schedule_summary: str
    accent_color: Optional[str] = None

    class Config:
        from_attributes = True

def transform_syllabus_to_response(syllabus: Syllabus) -> dict:
    """Transform database syllabus to frontend-compatible format"""
    import json
    
    try:
        print(f"Transforming syllabus {syllabus.id}: {syllabus.filename}")
        
        # Parse JSON strings back to objects
        midterm_dates = []
        if syllabus.midterm_dates:
            try:
                midterm_dates = json.loads(syllabus.midterm_dates)
            except:
                midterm_dates = []
        
        grading_policy = {}
        if syllabus.grading_policy:
            try:
                grading_policy = json.loads(syllabus.grading_policy)
            except:
                grading_policy = {}
        
        result = {
            "id": syllabus.id,
            "filename": syllabus.filename or "",
            "course_code": syllabus.course_code or "",
            "course_name": syllabus.course_name or "",
            "instructor": {
                "name": syllabus.instructor_name or "",
                "email": syllabus.instructor_email or ""
            },
            "term": {
                "semester": syllabus.semester or "",
                "year": syllabus.year or ""
            },
            "description": syllabus.description or "",
            "meeting_info": {
                "days": syllabus.meeting_days or "",
                "time": syllabus.meeting_time or "",
                "location": syllabus.meeting_location or ""
            },
            "important_dates": {
                "first_class": syllabus.first_class or "",
                "last_class": syllabus.last_class or "",
                "midterms": midterm_dates,
                "final_exam": syllabus.final_exam_date or ""
            },
            "grading_policy": grading_policy,
            "schedule_summary": syllabus.schedule_summary or "",
            "accent_color": syllabus.accent_color
        }
        
        print(f"Transformed result: {result}")
        return result
    except Exception as e:
        print(f"Error transforming syllabus {syllabus.id}: {str(e)}")
        # Return a minimal valid response
        return {
            "id": syllabus.id,
            "filename": getattr(syllabus, 'filename', ''),
            "course_code": "",
            "course_name": getattr(syllabus, 'course_name', ''),
            "instructor": {"name": "", "email": ""},
            "term": {"semester": "", "year": ""},
            "description": "",
            "meeting_info": {"days": "", "time": "", "location": ""},
            "important_dates": {"first_class": "", "last_class": "", "midterms": [], "final_exam": ""},
            "grading_policy": {},
            "schedule_summary": "",
            "accent_color": None
        }

router = APIRouter()

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

ACCEPTED_EXTENSIONS = {".pdf", ".docx" }

def is_allowed_file(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ACCEPTED_EXTENSIONS)

@router.post("/upload", response_model=UploadResponse)
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
        s3_file_name = f"syllabi/{current_user.id}/{uuid.uuid4()}_{file.filename}"
        s3_service.upload_file(file_content, s3_file_name, file.content_type)
        
        # Extract text from file
        text_content = extract_text(file_content, file.filename)
        
        # Extract syllabus information using Gemini
        syllabus_info = extract_syllabus_info(text_content)
        
        # Create syllabus record
        syllabus = Syllabus(
            user_id=current_user.id,
            filename=file.filename,
            content_type=file.content_type,
            s3_file_key=s3_file_name,  # Store the full S3 key
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
        
        # Return the expected UploadResponse format
        return UploadResponse(
            filename=file.filename,
            metadata={
                "title": syllabus_info.get('title', file.filename),
                "author": syllabus_info.get('instructor', {}).get('name', ''),
                "document_type": "syllabus",
                "date": datetime.now().isoformat(),
                "id": str(syllabus.id)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process syllabus: {str(e)}")

@router.get("/", response_model=List[SyllabusResponse])
async def get_syllabi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all syllabi for the current user."""
    try:
        syllabi = db.query(Syllabus).filter(Syllabus.user_id == current_user.id).all()
        result = []
        for syllabus in syllabi:
            try:
                transformed = transform_syllabus_to_response(syllabus)
                # Validate the transformed data against SyllabusResponse
                validated = SyllabusResponse(**transformed)
                result.append(validated.model_dump())
            except Exception as e:
                print(f"Error transforming syllabus {getattr(syllabus, 'id', 'unknown')}: {e}")
                continue
        return result
    except Exception as e:
        print(f"Error in get_syllabi: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch syllabi: {e}")

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify routing works."""
    return {"message": "Test endpoint working"}

@router.get("/test-empty")
async def test_empty_syllabi():
    """Test endpoint that returns empty syllabi list."""
    return []

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
    
    transformed = transform_syllabus_to_response(syllabus)
    return SyllabusResponse(**transformed)

@router.get("/{syllabus_id}/file")
async def get_syllabus_file_url(
    syllabus_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the file URL for a syllabus."""
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.user_id == current_user.id
    ).first()
    
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Generate S3 signed URL for the file
    if not syllabus.s3_file_key:
        raise HTTPException(status_code=404, detail="Syllabus file not found")
    
    try:
        file_url = s3_service.get_file_url(syllabus.s3_file_key)
        return {"file_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file URL: {str(e)}")

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

@router.patch("/{syllabus_id}/color")
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

@router.patch("/{syllabus_id}")
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

