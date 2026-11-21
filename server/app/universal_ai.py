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

class UniversalReportSchema(BaseModel):
    findings: list[BiomarkerItem]
    ml_insight: ClinicalInsight

def analyze_with_gemini(raw_text: str, age: int, gender: str) -> dict | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are an expert clinical laboratory data interpreter.
        Analyze the following medical report text for a {age}-year-old {gender} patient.
        
        Extract ALL numeric lab tests/biomarkers present in the report (e.g., CBC, Glucose, Lipid, Liver, Kidney, Thyroid, Urine, Electrolytes, Vitamins, etc.).
        For each test:
        - Determine accurate biological sex-calibrated normal reference range (min and max). If a range is written in the report, use that; otherwise use standard clinical reference values.
        - Classify status strictly as "LOW", "HIGH", or "NORMAL".
        - Provide a concise 1-sentence description of what the biomarker measures.
        - Provide a clear, patient-friendly interpretation.
        
        In `ml_insight`, provide an overall clinical pattern summary in `category` (e.g., "Anemia & Glycemic Risk Detected" or "Normal Clinical Profile") and a realistic confidence score (85.0 to 99.0).
        If the report is qualitative (like X-ray/Ultrasound without numbers), create 1 summary item with value=0, min=0, max=0, unit="Qualitative", status="NORMAL" or "HIGH" (if abnormal).

        Medical Report Text:
        \"\"\"{raw_text}\"\"\"
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UniversalReportSchema,
                temperature=0.1,
            ),
        )

        if response.text:
            parsed = json.loads(response.text)
            if parsed.get("findings"):
                return {
                    "patient": {"age": age, "gender": gender},
                    "extracted_text_preview": raw_text[:300],
                    "findings": parsed["findings"],
                    "ml_insight": parsed["ml_insight"]
                }
    except Exception as e:
        print(f"Gemini Universal AI fallback triggered: {e}")
    
    return None