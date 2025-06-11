import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def extract_syllabus_info(document_text: str) -> dict:
    # Trim large documents to avoid exceeding token limits
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
    "first_class": "",
    "last_class": "",
    "midterms": [],
    "final_exam": "",
  }},
  "grading_policy": {{
  }},
  "schedule_summary": ""
}}

INPUT SYLLABUS TEXT:
{trimmed_text}

Remember to:
1. Return ONLY the JSON object
2. Use actual values from the input text
3. Use empty strings ("") for missing text fields
4. Use empty arrays ([]) for missing lists
5. Use empty objects ({{}}) for missing nested objects
6. Do not include any explanatory text or markdown formatting
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
