import os
import uuid
import requests
import mimetypes
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile

from .pipeline import process_document
from .schema import ReportResponse

app = FastAPI(title="Bill Extraction API")

class InputSchema(BaseModel):
    document: str


@app.post("/extract-bill-data", response_model=ReportResponse)
async def extract_bill_data(payload: InputSchema):

    url = payload.document

    # Step 1: Create a temporary directory for this file
    tmp_dir = tempfile.mkdtemp(prefix="bfhl_")

    # --- FIX: Safe extension handling ---
    clean_url = url.split("?")[0]
    filename = os.path.basename(clean_url)

    # Extract extension safely
    if "." in filename:
        ext = filename.split(".")[-1].lower()
    else:
        ext = "pdf"   # Fallback

    # Accept only supported image/PDF types, fallback to PDF
    if ext not in ["pdf", "png", "jpg", "jpeg"]:
        ext = "pdf"

    file_path = os.path.join(tmp_dir, f"{uuid.uuid4()}.{ext}")

    # Step 2: Download file
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download file: {str(e)}"
        )

    # Step 3: Process the downloaded file
    try:
        result = process_document(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

    return result
