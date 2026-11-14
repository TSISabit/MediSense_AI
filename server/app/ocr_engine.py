import fitz  # PyMuPDF
import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text.strip()

def extract_text_from_image(file_bytes: bytes) -> str:
    np_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray, detail=0)
    return " ".join(results)