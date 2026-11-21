import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageOps

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text.strip()

def extract_text_from_image(file_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("L")
        # ডার্ক মোড স্ক্রিনশট হলে অটো ইনভার্ট করবে মাত্র 2MB RAM-এ
        if img.resize((1, 1)).getpixel((0, 0)) < 127:
            img = ImageOps.invert(img)
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        print(f"OCR error: {e}")
        return ""