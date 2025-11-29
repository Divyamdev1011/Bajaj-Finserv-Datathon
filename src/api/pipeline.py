import io
from PIL import Image
import numpy as np

from ..orc.gvision_extractor import extract_with_gvision
from ..preprocessing.image_cleaner import preprocess_image
from ..extraction.llm_parser import parse_with_llm
from ..utils.pdf_utils import convert_pdf_to_images
from .schema import ReportResponse, TokenUsage, DataModel, PageLineItems, BillItem


def load_image_bytes_to_cv2(img_bytes: bytes):
    """Convert raw PNG/JPG bytes → OpenCV numpy array."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def process_document(file_path: str):

    # Extract pages → list of images (bytes)
    pages = convert_pdf_to_images(file_path)

    pagewise_items = []
    total_token_usage = TokenUsage()
    total_items = 0

    for idx, page_img_bytes in enumerate(pages, start=1):

        # Convert bytes to CV2 image for preprocessing
        cv2_img = load_image_bytes_to_cv2(page_img_bytes)

        # Preprocess
        cleaned_img = preprocess_image(cv2_img)

        # OCR (Vision accepts bytes → reconvert cleaned image to bytes)
        pil_img = Image.fromarray(cleaned_img)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        cleaned_bytes = buf.getvalue()

        text = extract_with_gvision(cleaned_bytes)

        if not text:
            text = ""

        # LLM parse
        try:
            items = parse_with_llm(text) or []
        except Exception:
            items = []

        bill_items = []
        for i in items:
            name = i.get("item_name", "UNKNOWN")
            amt = float(i.get("item_amount", 0) or 0)
            rate = float(i.get("item_rate", 0) or 0)
            qty = float(i.get("item_quantity", 1) or 1)

            bill_items.append(
                BillItem(
                    item_name=name,
                    item_amount=amt,
                    item_rate=rate,
                    item_quantity=qty,
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
