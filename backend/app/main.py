from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException
from .services.gemini import extract_metadata_with_gemini
import shutil # handles high-level file operations
from dotenv import load_dotenv
import os
from .services.extractor import extract_text
from backend.app.db.database import SessionLocal
from sqlalchemy import text

ACCEPTED_EXTENSIONS = {".pdf", ".docx", ".txt" }

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
app = FastAPI()

UPLOAD_DIR = 'uploads' # local placeholder for dev and testing
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_allowed_file(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ACCEPTED_EXTENSIONS)

@app.post('/upload/')
async def upload_file(file: UploadFile = File(...)):
    if not is_allowed_file(file.filename.lower()):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and txt files are allowed"
        )
    # save the file locally to uploads/
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        extracted = extract_text(file_path)
        metadata = extract_metadata_with_gemini(extracted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    
    return { 
        'filename': file.filename,
        'extract_text': extracted[:300] + "...", # preview first 200 chars
        'metadata': metadata,
    }