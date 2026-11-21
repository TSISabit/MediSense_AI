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

def get_working_model(client) -> str:
    preferred = ["gemini-3.8-flash", "gemini-3-flash-preview", "gemini-2.5-flash"]
    try:
        available = [
            m.name.replace("models/", "")
            for m in client.models.list()
            if "generateContent" in (m.supported_actions or []) and "flash" in m.name.lower()
        ]
        for p in preferred:
            if p in available:
                return p
        if available:
            return available[0]
    except Exception:
        pass
    return "gemini-3.8-flash"

SYSTEM_PROMPT = """
You are MediSense AI, an advanced multimodal clinical diagnostic report interpreter.
Analyze the provided medical report (CBC, Biochemistry, Lipid, Liver, Kidney, Thyroid, Urine, Serology, ECG, X-Ray, Ultrasound, MRI, or Prescription) for a {age}-year-old {gender} patient.

Tasks:
1. Identify the `report_type` (e.g., "Complete Blood Count", "Liver & Renal Panel", "Chest X-Ray Report", "Thyroid Profile").
2. Extract ALL lab parameters/biomarkers present in the report:
   - If numeric: extract exact `value`, `unit`, and biological sex-calibrated `min` & `max` reference ranges (use ranges printed on the report if available, otherwise standard clinical ranges). Set `status` strictly to "LOW", "HIGH", or "NORMAL".
   - If qualitative/imaging (e.g., "Dengue NS1: Positive" or "Chest X-Ray: Mild pleural effusion"): set `value`: 1 (if abnormal/positive) or 0 (if normal/negative), `min`: 0, `max`: 0, `unit`: "Qualitative", and `status`: "HIGH" (for abnormal/positive) or "NORMAL".
3. In `ml_insight`:
   - `category`: Primary clinical finding or suspected condition pattern (e.g., "Iron-Deficiency Anemia & Mild Infection Risk", "Hypothyroidism Pattern", "Normal Health Screening").
   - `confidence`: Realistic confidence score (88.0 - 99.0).
   - `detailed_explanation`: A clear, empathetic, thorough 3-4 sentence explanation of what the overall report means in plain language.
   - `possible_conditions`: List of 1-3 potential medical conditions or clinical possibilities associated with the abnormal findings (or ["No abnormalities detected"] if normal).
   - `recommendations`: List of 2-3 actionable next steps (e.g., specific specialist to consult, hydration/dietary focus, or follow-up tests).
"""

def analyze_file_multimodal(file_bytes: bytes, mime_type: str, age: int, gender: str) -> dict | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        model_name = get_working_model(client)
        prompt = SYSTEM_PROMPT.format(age=age, gender=gender)

        response = client.models.generate_content(
            model=model_name,
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
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        model_name = get_working_model(client)
        prompt = SYSTEM_PROMPT.format(age=age, gender=gender) + f"\n\nReport Text:\n\"\"\"{raw_text}\"\"\""

        response = client.models.generate_content(
            model=model_name,
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