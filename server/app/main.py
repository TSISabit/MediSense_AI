import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ocr_engine import extract_text_from_image, extract_text_from_pdf
from app.nlp_analyzer import parse_and_analyze
from app.ml_model import get_ml_prediction, train_and_save_model
from app.universal_ai import (
    analyze_file_multimodal,
    analyze_text_universal,
    get_client,
    get_working_model,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    train_and_save_model()
    yield

app = FastAPI(title="MediSense AI Universal API", version="3.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"status": "online", "service": "MediSense AI Universal Multimodal Backend"}

@app.post("/api/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    age: int = Form(30),
    gender: str = Form("Male")
):
    if gender not in ["Male", "Female"]:
        raise HTTPException(status_code=400, detail="Gender must be Male or Female")

    file_bytes = await file.read()
    filename = file.filename.lower() if file.filename else ""

    if filename.endswith(".pdf"):
        mime_type = "application/pdf"
    elif filename.endswith(".png"):
        mime_type = "image/png"
    elif filename.endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"
    elif filename.endswith(".webp"):
        mime_type = "image/webp"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF, PNG, JPG, or WEBP.")

    # ১. Non-blocking Multimodal Vision AI (সর্বোচ্চ ২৫ সেকেন্ড টাইমআউটসহ)
    universal_result = await asyncio.to_thread(
        analyze_file_multimodal, file_bytes, mime_type, age, gender
    )
    if universal_result:
        return universal_result

    # ২. Fallback: OCR + Local Random Forest
    raw_text = await asyncio.to_thread(
        extract_text_from_pdf if mime_type == "application/pdf" else extract_text_from_image,
        file_bytes,
    )
    extracted_values, findings = parse_and_analyze(raw_text, gender)
    if not findings:
        raise HTTPException(status_code=422, detail="Could not extract recognizable clinical data from the report.")

    ml_insight = get_ml_prediction(age, gender, extracted_values)
    ml_insight["detailed_explanation"] = "Analyzed via local clinical reference engine."
    ml_insight["possible_conditions"] = [ml_insight["category"]]
    ml_insight["recommendations"] = ["Consult a qualified physician with your original lab report."]

    return {
        "patient": {"age": age, "gender": gender},
        "report_type": "Laboratory Report",
        "findings": findings,
        "ml_insight": ml_insight
    }

@app.post("/api/analyze-text")
async def analyze_text(payload: TextAnalysisRequest):
    if payload.gender not in ["Male", "Female"]:
        raise HTTPException(status_code=400, detail="Gender must be Male or Female")

    universal_result = await asyncio.to_thread(
        analyze_text_universal, payload.text, payload.age, payload.gender
    )
    if universal_result:
        return universal_result

    extracted_values, findings = parse_and_analyze(payload.text, payload.gender)
    if not findings:
        raise HTTPException(status_code=422, detail="No valid medical parameters found in text.")
    ml_insight = get_ml_prediction(payload.age, payload.gender, extracted_values)
    ml_insight["detailed_explanation"] = "Analyzed via local clinical reference engine."
    ml_insight["possible_conditions"] = [ml_insight["category"]]
    ml_insight["recommendations"] = ["Consult a physician for clinical correlation."]

    return {
        "patient": {"age": payload.age, "gender": payload.gender},
        "report_type": "Multi-Organ Health Panel",
        "findings": findings,
        "ml_insight": ml_insight
    }

def _run_chat_sync(payload: ChatRequest) -> str:
    client = get_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing on server.")
    model_name = get_working_model(client)
    prompt = f"""
    You are MediSense AI, an empathetic clinical report assistant.
    Patient: {payload.age}-year-old {payload.gender}.
    Analyzed Medical Report Data:
    {payload.report_context}

    User Question: {payload.message}

    Instructions:
    - Reply in the exact language the user used (Bangla if asked in Bangla, English if asked in English).
    - Explain clearly based on the patient's specific lab values and findings above.
    - Provide practical diet/lifestyle guidance and advise consulting a specialist doctor. Keep it clear and well-structured.
    """
    response = client.models.generate_content(
        model=model_name,
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