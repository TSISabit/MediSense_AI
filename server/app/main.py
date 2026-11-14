from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ocr_engine import extract_text_from_image, extract_text_from_pdf
from app.nlp_analyzer import parse_and_analyze
from app.ml_model import get_ml_prediction, train_and_save_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    train_and_save_model()
    yield

app = FastAPI(title="MediSense AI API", version="1.0.0", lifespan=lifespan)

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

@app.get("/")
def health_check():
    return {"status": "online", "service": "MediSense AI Backend"}

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
        raw_text = extract_text_from_pdf(file_bytes)
    elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        raw_text = extract_text_from_image(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF, PNG, or JPG.")

    extracted_values, findings = parse_and_analyze(raw_text, gender)
    if not findings:
        raise HTTPException(
            status_code=422,
            detail="Could not detect standard CBC parameters (Hemoglobin, WBC, Platelet, RBC) in the uploaded report."
        )

    ml_insight = get_ml_prediction(age, gender, extracted_values)

    return {
        "patient": {"age": age, "gender": gender},
        "extracted_text_preview": raw_text[:300],
        "findings": findings,
        "ml_insight": ml_insight
    }

@app.post("/api/analyze-text")
async def analyze_text(payload: TextAnalysisRequest):
    if payload.gender not in ["Male", "Female"]:
        raise HTTPException(status_code=400, detail="Gender must be Male or Female")
    extracted_values, findings = parse_and_analyze(payload.text, payload.gender)
    if not findings:
        raise HTTPException(status_code=422, detail="No valid CBC parameters found in text.")
    ml_insight = get_ml_prediction(payload.age, payload.gender, extracted_values)
    return {
        "patient": {"age": payload.age, "gender": payload.gender},
        "findings": findings,
        "ml_insight": ml_insight
    }