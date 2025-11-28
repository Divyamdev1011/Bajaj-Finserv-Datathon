"""
Image preprocessing utilities: denoise, threshold, resize, deskew helpers.
"""
from PIL import Image
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, th)
    return output_path

def simple_resize_if_large(input_path: str, output_path: str, max_side: int = 2000) -> str:
    img = Image.open(input_path)
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        nw, nh = int(w * scale), int(h * scale)
        img = img.resize((nw, nh))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    return output_path
