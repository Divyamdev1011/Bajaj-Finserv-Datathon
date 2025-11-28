"""
Overwrite/whitener detection basic stub using brightness anomalies.
"""
import cv2
import numpy as np

def detect_whitener_regions(image_path: str, threshold: int = 245):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return {'found': False, 'regions': []}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray > threshold
    if mask.sum() > 100:  # heuristic
        return {'found': True, 'coverage': float(mask.sum()) / mask.size}
    return {'found': False, 'coverage': 0.0}
