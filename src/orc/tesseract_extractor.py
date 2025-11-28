"""
Local Tesseract OCR using pytesseract. Supports input as file path (str) or image bytes.
Requires `tesseract` binary installed for full functionality.
"""
from PIL import Image
import pytesseract
from io import BytesIO
from typing import Union

def extract_text_from_image(image: Union[str, bytes]) -> str:
    if isinstance(image, (bytes, bytearray)):
        img = Image.open(BytesIO(image))
    else:
        img = Image.open(image)
    text = pytesseract.image_to_string(img)
    return text or "EXTRACTED TEXT FROM TESSERACT (no text)"
