import io
import numpy as np
from PIL import Image

# OCR imports
from ..orc.gvision_extractor import extract_with_gvision
from ..orc.tesseract_extractor import extract_text_from_image
from ..orc.textract_extractor import extract_text_from_pdf

# Preprocessing + utils
from ..preprocessing.image_cleaner import preprocess_image
from ..extraction.llm_parser import parse_with_llm
from ..utils.pdf_utils import convert_pdf_to_images

# Output schemas
from .schema import ReportResponse, TokenUsage, DataModel, PageLineItems, BillItem



def load_image_bytes_to_cv2(img_bytes: bytes):
    """Convert PNG/JPG bytes → NumPy array for preprocessing."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)



def process_document(file_path: str):
    """
    MASTER PIPELINE:
    PDF → images → preprocess → OCR → LLM → JSON output.
    """

    # Convert PDF to list of PNG/JPG page images
    pages = convert_pdf_to_images(file_path)
    print("DEBUG: Total pages detected =", len(pages))

    pagewise_items = []
    total_token_usage = TokenUsage()
    total_items = 0

    for idx, page_img_bytes in enumerate(pages, start=1):

        print(f"\n==================== PAGE {idx} ====================")

        # 1️⃣ Convert raw image bytes → CV2 numpy array
        cv2_img = load_image_bytes_to_cv2(page_img_bytes)

        # 2️⃣ Preprocess page (denoise, resize, threshold, etc.)
        cleaned_img = preprocess_image(cv2_img)

        # Convert cleaned image → PNG bytes for OCR
        pil_img = Image.fromarray(cleaned_img)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        cleaned_bytes = buf.getvalue()

        # -----------------------------------------------------
        # 3️⃣ OCR PIPELINE WITH FULL FALLBACK SYSTEM
        # -----------------------------------------------------

        # Try Google Vision
        text = extract_with_gvision(cleaned_bytes)
        print(f"DEBUG: Vision OCR for page {idx} (first 180 chars): {text[:180]}")

        # If Vision fails → Tesseract
        if not text or text.strip() == "":
            print(f"DEBUG: Page {idx}: Vision empty → using Tesseract OCR")
            text = extract_text_from_image(cleaned_bytes)
            print(f"DEBUG: Tesseract OCR for page {idx} (first 180 chars): {text[:180]}")

        # If Tesseract also fails → AWS Textract fallback
        if not text or text.strip() == "":
            print(f"DEBUG: Page {idx}: Tesseract empty → using Textract fallback")
            text = extract_text_from_pdf(file_path)
            print(f"DEBUG: Textract OCR for page {idx} (first 180 chars): {text[:180]}")

        if not text:
            print(f"DEBUG: Page {idx}: Still empty after ALL OCR layers → LLM may fail")

        # -----------------------------------------------------
        # 4️⃣ STRUCTURED EXTRACTION USING GEMINI FLASH 2.0
        # -----------------------------------------------------
        try:
            items = parse_with_llm(text) or []
        except Exception as e:
            print("LLM parse error:", e)
            items = []

        print(f"DEBUG: LLM extracted {len(items)} items for page {idx}")

        # -----------------------------------------------------
        # 5️⃣ BUILD PAGE JSON STRUCTURE
        # -----------------------------------------------------
        bill_items = []
        for item in items:
            name = item.get("item_name", "UNKNOWN")

            # Convert safely
            try:
                amt = float(item.get("item_amount", 0) or 0)
            except:
                amt = 0.0

            try:
                rate = float(item.get("item_rate", 0) or 0)
            except:
                rate = 0.0

            try:
                qty = float(item.get("item_quantity", 1) or 1)
            except:
                qty = 1.0

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

    # -----------------------------------------------------
    # 6️⃣ FINAL API RESPONSE
    # -----------------------------------------------------
    return ReportResponse(
        is_success=True,
        token_usage=total_token_usage,
        data=DataModel(
            pagewise_line_items=pagewise_items,
            total_item_count=total_items,
        ),
    )
