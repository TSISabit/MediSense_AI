# 🩺 MediSense AI — Intelligent Medical Report Analyzer

**MediSense AI** is a full-stack clinical report interpretation system designed to extract, parse, and analyze Complete Blood Count (CBC) biomarkers from PDF documents and scanned lab images. By combining Optical Character Recognition (OCR), gender-calibrated clinical reference ranges, and a Random Forest classifier, it translates complex medical lab numbers into clear, visual health insights.

> ⚠️ **Medical Disclaimer:** This application is developed strictly for academic, educational, and informational screening purposes. It is not a substitute for professional medical advice, diagnosis, or treatment.

---

## ✨ Key Features

- **Multi-Format Report Ingestion:** Supports both digital laboratory PDFs (`PyMuPDF`) and smartphone-captured report images (`OpenCV` + `EasyOCR`).
- **Gender-Calibrated Biomarker Extraction:** Uses structured Regex NLP pipelines to extract Hemoglobin, WBC, Platelet, and RBC counts, evaluating them against biological sex-specific clinical ranges.
- **Machine Learning Pattern Screening:** Utilizes a `Scikit-Learn` Random Forest classifier trained on age, sex, and hematological features to flag potential patterns (*Normal*, *Anemia-Related*, *Infection-Related*, *Thrombocytopenia-Risk*) with confidence scores.
- **Interactive Visual Range Bars:** Displays each biomarker on a color-coded clinical scale so users can immediately see where their values sit relative to healthy thresholds.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js (App Router), TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | Python 3.12, FastAPI, Uvicorn, Pydantic |
| **AI / ML & OCR** | Scikit-Learn (Random Forest), EasyOCR, OpenCV, PyMuPDF, Pandas, NumPy |
| **Deployment** | Vercel (Frontend), Render / Docker (Backend) |

---

## 🚀 Local Setup & Installation

### 1. Start the AI Backend (FastAPI)
```bash
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000