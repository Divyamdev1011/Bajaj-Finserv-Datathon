# BFHL Datathon - Invoice Extraction Pipeline

This repository is an end-to-end skeleton for the Bajaj Finserv Health (BFHL) Datathon.

Features:
- Preprocessing (OpenCV/Pillow)
- OCR provider stubs: AWS Textract, Google Vision, Tesseract
- LLM integration (OpenAI) with safe fallback
- Regex-based extraction fallback
- Totals calculator, duplicate handling, and validators
- FastAPI endpoint to expose the pipeline
- Unit tests and deployment Dockerfile

Quick start:
1. Create virtualenv and install requirements: `pip install -r requirements.txt`
2. Add provider credentials (optional)
3. Run tests: `pytest -q`
4. Run API: `uvicorn src.api.main:app --reload --port 8000`
5. POST file(s) to `/extract-bill-data`.

See docs/ for architecture and pitch deck template.

## Updated According to Official Datathon API

### Endpoint
POST /extract-bill-data

### Input JSON
{
  "document": "<url of bill>"
}

### Output JSON (Must follow exactly)
{
  "is_success": true,
  "token_usage": {...},
  "data": {
    "pagewise_line_items": [...],
    "total_item_count": 0
  }
}

This repository follows the exact datathon structure:
- Page-wise processing
- Google Vision OCR
- LLM-based extraction (item_name, item_amount, item_rate, item_quantity)
- Token usage tracking
