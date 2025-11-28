import io
try:
    from google.cloud import vision
    _HAS_GVISION = True
except Exception:
    _HAS_GVISION = False

def extract_with_gvision(image_bytes: bytes) -> str:
    """
    Accepts PNG/JPEG image bytes and returns the OCR'ed text using Google Vision.
    If Google Vision is not configured, return an empty string.
    """
    if not _HAS_GVISION:
        return ""

    client = vision.ImageAnnotatorClient()
    image_obj = vision.Image(content=image_bytes)
    response = client.text_detection(image=image_obj)

    if getattr(response, 'error', None) and getattr(response.error, 'message', None):
        return ""

    if response.text_annotations:
        return response.text_annotations[0].description

    return ""
