from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, uuid, shutil
from .pipeline import process_document

app = FastAPI(title='BFHL Datathon Extractor')

@app.post('/extract')
async def extract(file: UploadFile = File(...)):
    tmp_dir = '/tmp/bfhl'
    os.makedirs(tmp_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tmp_dir, file_id + '_' + file.filename)
    try:
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    result = process_document(file_path)
    return JSONResponse(result)
