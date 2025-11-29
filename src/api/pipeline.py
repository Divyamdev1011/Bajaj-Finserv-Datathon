import io
import os
from PIL import Image
import numpy as np

from ..orc.tesseract_extractor import extract_text_from_image
from ..preprocessing.image_cleaner import preprocess_image
from ..extraction.llm_parser import parse_with_llm
from ..utils.pdf_utils import convert_pdf_to_images

from .schema import ReportResponse, TokenUsage, DataModel, PageLineItems, BillItem


def load_image_bytes_to_cv2(img_bytes: bytes):
    """Convert PNG/JPG bytes → numpy array."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def load_document(file_path: str):
    """Return list of image bytes whether PDF, PNG, or JPG."""
    ext = file_path.lower().split(".")[-1]

    # PDF → multiple pages
    if ext == "pdf":
        return convert_pdf_to_images(file_path)

    # PNG/JPG → single page
    if ext in ["png", "jpg", "jpeg"]:
        with open(file_path, "rb") as f:
            return [f.read()]

    return []


def process_document(file_path: str):

    pages = load_document(file_path)

    if not pages:
        return ReportResponse(
            is_success=True,
            token_usage=TokenUsage(),
            data=DataModel(
                pagewise_line_items=[],
                total_item_count=0,
            )
        )

    pagewise_items = []
    total_token_usage = TokenUsage()
    total_items = 0

    for idx, page_img_bytes in enumerate(pages, start=1):

        # Convert bytes → numpy image for preprocessing
        cv2_img = load_image_bytes_to_cv2(page_img_bytes)

        # Preprocess for better OCR
        cleaned_img = preprocess_image(cv2_img)

        # Convert back to PNG bytes
        pil_img = Image.fromarray(cleaned_img)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        cleaned_bytes = buf.getvalue()

        # --- OCR TEXT EXTRACTION ---
        text = extract_text_from_image(cleaned_bytes)

        if not text:
            text = ""

        # --- LLM PARSING WITH GEMINI ---
        try:
            items = parse_with_llm(text) or []
        except Exception:
            items = []

        bill_items = []
        for i in items:
            name = i.get("item_name", "UNKNOWN")

            def safe_float(v, default):
                try:
                    return float(v or default)
                except:
                    return default

            bill_items.append(
                BillItem(
                    item_name=name,
                    item_amount=safe_float(i.get("item_amount"), 0.0),
                    item_rate=safe_float(i.get("item_rate"), 0.0),
                    item_quantity=safe_float(i.get("item_quantity"), 1.0),
                )
            )

        page_entry = PageLineItems(
            page_no=str(idx),
            page_type="Bill Detail",
            bill_items=bill_items,
        )

        pagewise_items.append(page_entry)
        total_items += len(bill_items)

    return ReportResponse(
        is_success=True,
        token_usage=total_token_usage,
        data=DataModel(
            pagewise_line_items=pagewise_items,
            total_item_count=total_items,
        ),
    )
