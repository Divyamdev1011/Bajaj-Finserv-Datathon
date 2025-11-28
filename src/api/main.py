import os
import uuid
import requests
import tempfile
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .pipeline import process_document
from .schema import ReportResponse

app = FastAPI(title="Bill Extraction API")

class InputSchema(BaseModel):
    document: str

@app.post("/extract-bill-data", response_model=ReportResponse)
async def extract_bill_data(payload: InputSchema):

    url = payload.document

    # Create temporary directory for the request; will be cleaned up automatically
    with tempfile.TemporaryDirectory(prefix="bfhl_") as tmp_dir:
        # Temporary file path
        file_path = os.path.join(tmp_dir, str(uuid.uuid4()) + ".pdf")

    # Step 1: Download the file
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Save as a file
        with open(file_path, "wb") as f:
            f.write(response.content)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document URL")

        # Step 2: Run pipeline
        try:
            result = process_document(file_path)
        except Exception:
            raise HTTPException(status_code=500, detail="Processing failed")

        return result
