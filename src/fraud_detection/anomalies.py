"""
Aggregate fraud detection responses.
"""
from .font_analyzer import detect_font_inconsistency
from .overwrite_detector import detect_whitener_regions

def analyze(image_path: str):
    res1 = detect_font_inconsistency(image_path)
    res2 = detect_whitener_regions(image_path)
    return {'font': res1, 'whitener': res2}
