import os
import fitz # lib for pdf manipulation
import docx

import io

def extract_text(file_content: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        return extract_from_pdf(file_content)
    elif ext == '.docx':
        return extract_from_docx(file_content)
    elif ext == '.txt':
        return extract_from_txt(file_content)
    else:
        raise ValueError('Unsupported file type')
    
def extract_from_pdf(file_content: bytes) -> str:
    text = ''
    with fitz.open(stream=file_content, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_from_docx(file_content: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_content))
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_from_txt(file_content: bytes) -> str:
    return file_content.decode('utf-8')