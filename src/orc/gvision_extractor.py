import os
import json
from google.cloud import vision
from google.oauth2 import service_account


def load_credentials():
    """
    Load service account JSON from environment variable.
    This is the only method that works on Render.
    """
    cred_str = os.getenv("GCV_CRED_JSON")
    if not cred_str:
        print("ERROR: GCV_CRED_JSON env variable missing!")
        return None

    try:
        data = json.loads(cred_str)
        return service_account.Credentials.from_service_account_info(data)
    except Exception as e:
        print("ERROR loading Google Vision credentials:", e)
        return None


# Create client at import time
_CREDENTIALS = load_credentials()
_CLIENT = None

if _CREDENTIALS:
    try:
        _CLIENT = vision.ImageAnnotatorClient(credentials=_CREDENTIALS)
    except Exception as e:
        print("ERROR creating Google Vision client:", e)
        _CLIENT = None


def extract_with_gvision(image_bytes: bytes) -> str:
    """
    Run Google Vision OCR. Works on Render.
    Returns empty string if Vision is not available.
    """
    if not _CLIENT:
        print("DEBUG: No Google Vision client. Returning empty OCR.")
        return ""

    try:
        image_obj = vision.Image(content=image_bytes)
        response = _CLIENT.text_detection(image=image_obj)

        if response.error and response.error.message:
            print("GVISION ERROR:", response.error.message)
            return ""

        if response.text_annotations:
            return response.text_annotations[0].description

        return ""

    except Exception as e:
        print("GVISION EXCEPTION:", e)
        return ""
