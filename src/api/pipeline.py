import fitz  # PyMuPDF
from ..ocr.textract_extractor import extract_with_textract
from ..ocr.gvision_extractor import extract_with_gvision
from ..preprocessing.image_cleaner import preprocess_image
from ..extraction.llm_parser import extract_items_llm
from ..utils.pdf_utils import convert_pdf_to_images
from .schema import ReportResponse, TokenUsage, DataModel, PageLineItems, BillItem

def process_document(file_path: str):

    pages = convert_pdf_to_images(file_path)

    pagewise_items = []
    total_token_usage = TokenUsage()
    total_items = 0

    for idx, page_img in enumerate(pages, start=1):

        # Preprocess page
        cleaned_img = preprocess_image(page_img)

        # OCR
        text = extract_with_gvision(cleaned_img)

        # LLM parse
        items, usage = extract_items_llm(text)

        # Update token usage
        total_token_usage.total_tokens += usage.total_tokens
        total_token_usage.input_tokens += usage.input_tokens
        total_token_usage.output_tokens += usage.output_tokens

        # Build response
        bill_items = [
            BillItem(
                item_name=i["item_name"],
                item_amount=float(i["item_amount"]),
                item_rate=float(i["item_rate"]),
                item_quantity=float(i["item_quantity"])
            )
            for i in items
        ]

        page_entry = PageLineItems(
            page_no=str(idx),
            page_type="Bill Detail",
            bill_items=bill_items
        )

        pagewise_items.append(page_entry)
        total_items += len(items)

    # Final response
    return ReportResponse(
        is_success=True,
        token_usage=total_token_usage,
        data=DataModel(
            pagewise_line_items=pagewise_items,
            total_item_count=total_items
        )
    )
