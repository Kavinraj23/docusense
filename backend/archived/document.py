from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.db.models.document import Document
from app.services.gemini import extract_metadata_with_gemini
from app.services.extractor import extract_text
import shutil, os

router = APIRouter()

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

ACCEPTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_allowed_file(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ACCEPTED_EXTENSIONS)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not is_allowed_file(file.filename.lower()):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are allowed"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted = extract_text(file_path)
        metadata = extract_metadata_with_gemini(extracted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_doc = Document(
    filename=file.filename,
    content_type=file.content_type,
    title=metadata.get("title"),
    author=metadata.get("author"),
    document_type=metadata.get("document_type"),
    date=metadata.get("date"),
    summary=metadata.get("summary"),
    tags=",".join(metadata.get("tags", [])),  # Convert list to CSV
)

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {
        "filename": file.filename,
        "document_id": new_doc.id,
        "extract_text": extracted[:300] + "...",
        "metadata": metadata,
    }

@router.get("/documents", response_model=List[dict])
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return [
        # inside the list comprehension
        {
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "upload_time": doc.upload_time.isoformat(),
            "title": doc.title,
            "summary": doc.summary,
            "keywords": doc.tags,
        }
        for doc in documents
    ]