from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from typing import List
import json
import shutil
import os
from app.db.session import SessionLocal
from app.db.models.syllabus import Syllabus
from app.services.gemini import extract_syllabus_info
from app.services.extractor import extract_text
from pydantic import BaseModel
from app.services.security import get_current_user  # <-- Import the auth dependency
from app.db.deps import get_db

class ColorUpdate(BaseModel):
    accent_color: str

class ImportantDates(BaseModel):
    first_class: str
    last_class: str
    midterms: List[str]
    final_exam: str

class SyllabusUpdate(BaseModel):
    important_dates: ImportantDates

router = APIRouter()

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

ACCEPTED_EXTENSIONS = {".pdf", ".docx" }

def is_allowed_file(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ACCEPTED_EXTENSIONS)

@router.post("/upload")
async def upload_syllabus(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- Require authentication
):
    if not is_allowed_file(file.filename.lower()):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX and TXT files are allowed"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text(file_path)
        metadata = extract_syllabus_info(extracted_text)

        # Transform the nested Gemini response into flat model fields
        instructor_info = metadata.get("instructor", {})
        term_info = metadata.get("term", {})
        meeting_info = metadata.get("meeting_info", {})
        important_dates = metadata.get("important_dates", {})
        
        new_syllabus = Syllabus(
            filename=file.filename,
            content_type=file.content_type,
            course_code=metadata.get("course_code"),
            course_name=metadata.get("course_name"),
            instructor_name=instructor_info.get("name"),
            instructor_email=instructor_info.get("email"),
            semester=term_info.get("semester"),
            year=term_info.get("year"),
            description=metadata.get("description"),
            
            # Meeting information
            meeting_days=meeting_info.get("days"),
            meeting_time=meeting_info.get("time"),
            meeting_location=meeting_info.get("location"),
            
            # Important dates
            first_class=important_dates.get("first_class"),
            last_class=important_dates.get("last_class"),
            midterm_dates=json.dumps(important_dates.get("midterms", [])),
            final_exam_date=important_dates.get("final_exam"),
            
            # Grading and schedule
            grading_policy=json.dumps(metadata.get("grading_policy", {})),
            schedule_summary=metadata.get("schedule_summary")
        )

        db.add(new_syllabus)
        db.commit()
        db.refresh(new_syllabus)

        return {
            "filename": file.filename,
            "syllabus_id": new_syllabus.id,
            "metadata": metadata
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing syllabus: {str(e)}")

@router.get("/syllabi", response_model=List[dict])
def list_syllabi(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- Require authentication
):
    syllabi = db.query(Syllabus).all()
    return [
        {
            "id": syllabus.id,
            "filename": syllabus.filename,
            "course_code": syllabus.course_code,
            "course_name": syllabus.course_name,
            "instructor": {
                "name": syllabus.instructor_name,
                "email": syllabus.instructor_email
            },
            "term": {
                "semester": syllabus.semester,
                "year": syllabus.year
            },
            "description": syllabus.description,
            "meeting_info": {
                "days": syllabus.meeting_days,
                "time": syllabus.meeting_time,
                "location": syllabus.meeting_location
            },
            "important_dates": {
                "first_class": syllabus.first_class,
                "last_class": syllabus.last_class,
                "midterms": json.loads(syllabus.midterm_dates) if syllabus.midterm_dates else [],
                "final_exam": syllabus.final_exam_date
            },
            "grading_policy": json.loads(syllabus.grading_policy) if syllabus.grading_policy else {},
            "schedule_summary": syllabus.schedule_summary,
            "accent_color": syllabus.accent_color
        }
        for syllabus in syllabi
    ]

@router.delete("/syllabi/{syllabus_id}")
def delete_syllabus(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- Require authentication
):
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Delete the associated file if it exists
    file_path = os.path.join(UPLOAD_DIR, syllabus.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            # Log the error but continue with DB deletion
            print(f"Error deleting file: {file_path}")
    
    # Delete from database
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
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
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
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Update important dates
    syllabus.first_class = syllabus_update.important_dates.first_class
    syllabus.last_class = syllabus_update.important_dates.last_class
    syllabus.midterm_dates = json.dumps(syllabus_update.important_dates.midterms)
    syllabus.final_exam_date = syllabus_update.important_dates.final_exam
    
    db.commit()
    return {"status": "success"}