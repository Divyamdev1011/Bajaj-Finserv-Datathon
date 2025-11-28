import os
import uuid
import requests
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

    # Create temp directory
    tmp_dir = "/tmp/bfhl"
    os.makedirs(tmp_dir, exist_ok=True)

    # Temporary file path
    file_path = os.path.join(tmp_dir, str(uuid.uuid4()) + ".pdf")

    # Step 1: Download the file
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("URL did not return file")

        with open(file_path, "wb") as f:
            f.write(response.content)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document URL")

    # Step 2: Run pipeline
    result = process_document(file_path)

    return result
