import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def extract_metadata_with_gemini(document_text: str) -> dict:
    # Trim large documents to avoid exceeding token limits
    trimmed_text = document_text[:8000]

    # Prompt for structured metadata in JSON
    prompt = f"""
You are a document parsing assistant. Extract metadata from the document below and return the output in **valid JSON format**, without markdown backticks or formatting.

Required fields:
- title: (string)
- author: (string, or "Unknown" if not found)
- document_type: (string, e.g., Resume, Report, Legal Form, Article)
- date: (string, if present in the document, else "Unknown")
- summary: (2–4 sentence summary of the document)
- tags: (list of relevant keywords or concepts. Please pick 5 of the best)

Document:
{trimmed_text}
"""

    # Use Gemini 1.5 Flash
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    raw = response.text.strip()

    # Clean up markdown-style code blocks like ```json ... ```
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)  # remove starting ``` or ```json
        raw = re.sub(r"\s*```$", "", raw)          # remove ending ```

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse JSON from Gemini response",
            "raw_response": response.text
        }
