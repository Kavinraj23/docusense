import os
import fitz # lib for pdf manipulation
import docx

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return extract_from_pdf(file_path)
    elif ext == '.docx':
        return extract_from_docx(file_path)
    elif ext == '.txt':
        return extract_from_txt(file_path)
    else:
        raise ValueError('Unsupported file type')
    
def extract_from_pdf(file_path: str) -> str:
    text = ''
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_from_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()