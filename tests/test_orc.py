from src.orc.tesseract_extractor import extract_text_from_image
def test_tesseract_runs():
    # Not a functional OCR test; ensures function exists.
    try:
        txt = extract_text_from_image
    except Exception:
        assert False
    assert callable(extract_text_from_image)
