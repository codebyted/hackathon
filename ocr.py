#ocr.py
import base64
import tempfile
import pytesseract
from PIL import Image
import io

def extract_text_from_base64(base64_img: str):
    try:
        image_data = base64.b64decode(base64_img)
        image = Image.open(io.BytesIO(image_data))

        # Preprocess
        image = image.convert("L")

        text = pytesseract.image_to_string(image)
        return {"text": text.strip(), "success": True}

    except Exception as e:
        return {"text": "", "error": str(e), "success": False}