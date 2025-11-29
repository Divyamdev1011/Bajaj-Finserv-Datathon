import os
import json
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load model
model = genai.GenerativeModel("gemini-2.0-flash")


EXTRACTION_PROMPT = """
You are a hospital bill expert. Extract ONLY actual bill line items from OCR text.

STRICT RULES:
- Extract ONLY rows that contain *actual billed items*.
- DO NOT extract dates, times, bill numbers, MRN, UHID, doctor names, GST numbers.
- DO NOT extract headers like 'Description', 'Qty', 'Rate', 'Amount'.
- DO NOT extract totals, subtotals, taxes, rounding, or discounts.
- Item name = EXACT text from bill.
- item_amount = net amount only.
- item_rate = per-unit price.
- item_quantity = numeric quantity.
- If amount/rate/qty missing → use 0.
- Output must be ONLY valid JSON array. No comments. No explanations.

OUTPUT JSON FORMAT EXAMPLE:
[
  {
    "item_name": "Paracetamol 500mg",
    "item_amount": 48.00,
    "item_rate": 8.00,
    "item_quantity": 6
  }
]
"""

def parse_with_llm(text: str):
    """Run Gemini Flash 2.0 to extract structured line item data."""

    if not text or text.strip() == "":
        return []

    try:
        response = model.generate_content(
            EXTRACTION_PROMPT + "\n\nOCR_TEXT:\n" + text,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 2048
            }
        )

        content = response.text.strip()

        # Try to parse raw JSON first
        try:
            return json.loads(content)
        except:
            pass

        # If the model returns JSON inside code fences
        import re
        json_match = re.search(r"\[[\s\S]*\]", content)
        if json_match:
            return json.loads(json_match.group(0))

        return []

    except Exception as e:
        print("Gemini LLM error:", e)
        return []
