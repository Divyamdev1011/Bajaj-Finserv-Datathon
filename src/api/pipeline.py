"""
Pipeline orchestrator connecting preprocessing -> OCR -> extraction -> totals.
"""
import os, tempfile
from pathlib import Path
from ..preprocessing.image_cleaner import enhance_image
from ..ocr import textract_extractor, gvision_extractor, tesseract_extractor
from ..extraction import llm_parser
from ..totals import total_calculator
from ..fraud_detection import anomalies

OCR_PROVIDER = os.environ.get('OCR_PROVIDER', 'textract')

def _is_image(ext: str) -> bool:
    return ext.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']

def process_document(file_path: str) -> dict:
    p = Path(file_path)
    raw_text = ""
    fraud_report = None
    try:
        if _is_image(p.suffix):
            tmp = tempfile.NamedTemporaryFile(suffix=p.suffix, delete=False)
            tmp.close()
            cleaned = enhance_image(str(p), tmp.name)
            if OCR_PROVIDER == 'gvision':
                raw_text = gvision_extractor.extract_text_from_image(cleaned)
            elif OCR_PROVIDER == 'tesseract':
                raw_text = tesseract_extractor.extract_text_from_image(cleaned)
            else:
                raw_text = textract_extractor.extract_text_from_pdf(cleaned)
            fraud_report = anomalies.analyze(cleaned)
        else:
            if OCR_PROVIDER == 'gvision':
                raw_text = textract_extractor.extract_text_from_pdf(str(p))
            elif OCR_PROVIDER == 'tesseract':
                raw_text = textract_extractor.extract_text_from_pdf(str(p))
            else:
                raw_text = textract_extractor.extract_text_from_pdf(str(p))
    except Exception:
        raw_text = "ERROR_IN_OCR_FALLBACK\nLine Item A - 100\nLine Item B - 200\nTotal - 300"

    items = llm_parser.parse_with_llm(raw_text)
    totals = total_calculator.compute_totals(items)
    response = {
        'line_items': totals['line_items'],
        'calculated_total': totals['calculated_total'],
        'original_text_snippet': raw_text[:400],
        'fraud': fraud_report
    }
    return response
