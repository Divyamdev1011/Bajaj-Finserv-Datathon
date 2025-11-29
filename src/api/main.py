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

    # Step 1: Create a temporary directory that persists through processing
    tmp_dir = tempfile.mkdtemp(prefix="bfhl_")

    # Detect file extension from URL
    ext = url.split("?")[0].split(".")[-1].lower()

    if ext not in ["pdf", "png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_path = os.path.join(tmp_dir, f"{uuid.uuid4()}.{ext}")

    # Step 2: Download file
    try:
        response = requests.get(url, timeout=15)
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
