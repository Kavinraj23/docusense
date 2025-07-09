import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def extract_syllabus_info(document_text: str) -> dict:    # Trim large documents to avoid exceeding token limits
    max_token_length = 20000
    trimmed_text = document_text[:max_token_length]
    
    prompt = f"""You are a syllabus parsing assistant. Extract metadata from the syllabus text below and return ONLY a valid JSON object. For any missing information, use empty strings or empty arrays. Do not include any explanatory text or markdown formatting in your response.

Here is an example of the output format (replace with actual values from the input syllabus):
{{
  "course_code": "",
  "course_name": "",
  "instructor": {{
    "name": "",
    "email": ""
  }},
  "term": {{
    "semester": "",
    "year": ""
  }},
  "description": "",
  "meeting_info": {{
    "days": "",
    "time": "",
    "location": ""
  }},
  "important_dates": {{
    "first_class": "2025-01-15",
    "last_class": "2025-05-01",
    "midterms": ["2025-02-15", "2025-03-15"],
    "final_exam": "2025-05-10"
  }},
  "grading_policy": {{
  }},
  "schedule_summary": ""
}}

INPUT SYLLABUS TEXT:
{trimmed_text}

CRITICAL DATE FORMATTING INSTRUCTIONS:
1. ALL dates must be in ISO 8601 format: "YYYY-MM-DD"
2. ALL dates must include the year explicitly
3. Use the year from the term for all dates (e.g., if term is "Spring 2025", all dates should be in 2025)
4. If no year is specified in the syllabus, use 2025 as the default year
5. If a date appears without a year, apply these rules:
   - For Spring term: Use January-May of the term year
   - For Fall term: Use August-December of the term year
   - For Summer term: Use June-July of the term year
6. Never output dates before year 2024
7. For dates like "Monday, January 15", add the appropriate year and convert to "2025-01-15"
8. If no specific date is found, use empty string "" instead of default dates

General Instructions:
1. Return ONLY the JSON object
2. Use actual values from the input text
3. Use empty strings ("") for missing text fields
4. Use empty arrays ([]) for missing lists
5. Use empty objects ({{}}) for missing nested objects
6. Do not include any explanatory text or markdown formatting
7. If the semester is not specified, reasonably assume whether it's fall, spring, or summer based on the context
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
