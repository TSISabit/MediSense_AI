import asyncio
import base64
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ocr_engine import extract_text_from_image, extract_text_from_pdf
from app.nlp_analyzer import parse_and_analyze
from app.universal_ai import (
    ACTIVE_MODEL,
    analyze_file_multimodal,
    analyze_text_universal,
    get_client,
)

app = FastAPI(title="MediSense AI Universal API", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Base64FileRequest(BaseModel):
    file_base64: str
    mime_type: str
    age: int = 30
    gender: str = "Male"

class TextAnalysisRequest(BaseModel):
    text: str
    age: int = 30
    gender: str = "Male"

class ChatRequest(BaseModel):
    message: str
    report_context: str
    age: int = 30
    gender: str = "Male"

@app.get("/")
def health_check():
    return {"status": "online", "service": "MediSense AI Universal Backend v4"}

@app.post("/api/analyze-base64")
async def analyze_base64(payload: Base64FileRequest):
    try:
        # Data URL হেডার থাকলে কেটে শুধু Base64 অংশ নেবে
        b64_data = payload.file_base64.split(",")[-1]
        file_bytes = base64.b64decode(b64_data)

        universal_result = await asyncio.to_thread(
            analyze_file_multimodal, file_bytes, payload.mime_type, payload.age, payload.gender
        )
        if universal_result:
            return universal_result

        # Fallback OCR
        raw_text = await asyncio.to_thread(
            extract_text_from_pdf if payload.mime_type == "application/pdf" else extract_text_from_image,
            file_bytes,
        )
        _, findings = parse_and_analyze(raw_text, payload.gender)
        if not findings:
            raise HTTPException(
                status_code=422,
                detail="Gemini AI could not read this file. Check Render logs for GEMINI_API_KEY or model error.",
            )

        return {
            "patient": {"age": payload.age, "gender": payload.gender},
            "report_type": "Laboratory Report (OCR Fallback)",
            "findings": findings,
            "ml_insight": {
                "category": "Clinical Parameter Screening",
                "confidence": 85.0,
                "detailed_explanation": "Analyzed via local OCR fallback engine.",
                "possible_conditions": ["Review abnormal parameters below"],
                "recommendations": ["Consult a physician with your original lab report."],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/analyze-text")
async def analyze_text(payload: TextAnalysisRequest):
    universal_result = await asyncio.to_thread(
        analyze_text_universal, payload.text, payload.age, payload.gender
    )
    if universal_result:
        return universal_result

    _, findings = parse_and_analyze(payload.text, payload.gender)
    if not findings:
        raise HTTPException(status_code=422, detail="No valid medical parameters found.")
    return {
        "patient": {"age": payload.age, "gender": payload.gender},
        "report_type": "Multi-Organ Health Panel",
        "findings": findings,
        "ml_insight": {
            "category": "Clinical Screening",
            "confidence": 85.0,
            "detailed_explanation": "Analyzed via local reference engine.",
            "possible_conditions": ["See flagged biomarkers"],
            "recommendations": ["Consult a specialist doctor."],
        },
    }

def _run_chat_sync(payload: ChatRequest) -> str:
    client = get_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing on server.")
    prompt = f"""
    You are MediSense AI, an empathetic clinical report assistant.
    Patient: {payload.age}-year-old {payload.gender}.
    Analyzed Medical Report Data:
    {payload.report_context}

    User Question: {payload.message}

    Instructions:
    - Reply in the exact language the user used (Bangla if asked in Bangla, English if asked in English).
    - Explain clearly based on the patient's specific lab values and findings above.
    - Provide practical diet/lifestyle guidance and advise consulting a specialist doctor.
    """
    response = client.models.generate_content(
        model=ACTIVE_MODEL,
        contents=prompt,
    )
    return response.text or ""

@app.post("/api/chat")
async def chat_with_report(payload: ChatRequest):
    try:
        reply = await asyncio.to_thread(_run_chat_sync, payload)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")