import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel

class BiomarkerItem(BaseModel):
    test: str
    value: float
    unit: str
    min: float
    max: float
    status: str  # "LOW", "HIGH", or "NORMAL"
    description: str
    interpretation: str

class ClinicalInsight(BaseModel):
    category: str
    confidence: float
    detailed_explanation: str
    possible_conditions: list[str]
    recommendations: list[str]

class UniversalReportSchema(BaseModel):
    report_type: str
    findings: list[BiomarkerItem]
    ml_insight: ClinicalInsight

# নতুন API Key-এর জন্য Google-এর নির্দেশিত সঠিক মডেল
ACTIVE_MODEL = "gemini-3.8-flash"

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are MediSense AI, a clinical diagnostic report interpreter.
Analyze the medical report for a {age}-year-old {gender} patient.
Extract ALL lab parameters/biomarkers (numeric or qualitative).
- For numeric tests: extract exact value, unit, and sex-calibrated min/max reference ranges. Set status to "LOW", "HIGH", or "NORMAL".
- For qualitative/imaging findings: set value=1 (if abnormal/positive) or 0 (if normal), min=0, max=0, unit="Qualitative", status="HIGH" or "NORMAL".
- Provide clear patient-friendly descriptions, interpretations, possible conditions, and actionable recommendations.
"""

def analyze_file_multimodal(file_bytes: bytes, mime_type: str, age: int, gender: str) -> dict | None:
    client = get_client()
    if not client:
        return None

    try:
        prompt = SYSTEM_PROMPT.format(age=age, gender=gender)
        response = client.models.generate_content(
            model=ACTIVE_MODEL,
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UniversalReportSchema,
                temperature=0.1,
            ),
        )

        if response.text:
            parsed = json.loads(response.text)
            return {
                "patient": {"age": age, "gender": gender},
                "report_type": parsed.get("report_type", "Medical Diagnostic Report"),
                "findings": parsed.get("findings", []),
                "ml_insight": parsed["ml_insight"],
            }
    except Exception as e:
        print(f"Multimodal Gemini error: {e}")

    return None

def analyze_text_universal(raw_text: str, age: int, gender: str) -> dict | None:
    client = get_client()
    if not client:
        return None

    try:
        prompt = SYSTEM_PROMPT.format(age=age, gender=gender) + f"\n\nReport Text:\n\"\"\"{raw_text}\"\"\""
        response = client.models.generate_content(
            model=ACTIVE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UniversalReportSchema,
                temperature=0.1,
            ),
        )

        if response.text:
            parsed = json.loads(response.text)
            return {
                "patient": {"age": age, "gender": gender},
                "report_type": parsed.get("report_type", "Medical Diagnostic Report"),
                "findings": parsed.get("findings", []),
                "ml_insight": parsed["ml_insight"],
            }
    except Exception as e:
        print(f"Text Gemini error: {e}")

    return None