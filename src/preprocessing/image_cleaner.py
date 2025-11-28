"""
Image preprocessing utilities: denoise, threshold, resize, deskew helpers.
"""
from PIL import Image
from io import BytesIO
import logging
import cv2
import numpy as np
import os

def enhance_image(input_path: str, output_path: str) -> str:
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not read image: {input_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    th = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 15, 8)
    odir = os.path.dirname(output_path)
    if odir:
        os.makedirs(odir, exist_ok=True)
    cv2.imwrite(output_path, th)
    return output_path

def simple_resize_if_large(input_path: str, output_path: str, max_side: int = 2000) -> str:
    img = Image.open(input_path)
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        nw, nh = int(w * scale), int(h * scale)
        img = img.resize((nw, nh))
    odir = os.path.dirname(output_path)
    if odir:
        os.makedirs(odir, exist_ok=True)
    img.save(output_path)
    return output_path

def preprocess_image(image_bytes: bytes, max_side: int = 2000) -> bytes:
    """
    Preprocess an in-memory image (bytes) and return processed image bytes (PNG).
    This function resizes the image if too large and converts to a binarized image.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
    except Exception as e:
        raise ValueError("Could not open image bytes for preprocessing") from e

    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        nw, nh = int(w * scale), int(h * scale)
        img = img.resize((nw, nh))

    # Convert to grayscale and binarize using a simple threshold
    img = img.convert('L')
    arr = np.array(img)
    # Simple adaptive thresholding fallback
    try:
        import cv2
        th = cv2.adaptiveThreshold(arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 15, 8)
        img = Image.fromarray(th)
    except Exception:
        # If OpenCV is not available, do a crude threshold with PIL
        img = img.point(lambda p: 255 if p > 200 else 0)

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
