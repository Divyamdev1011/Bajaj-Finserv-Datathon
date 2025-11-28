from ..orc.textract_extractor import extract_text_from_pdf
from ..orc.gvision_extractor import extract_with_gvision
from ..preprocessing.image_cleaner import preprocess_image
from ..extraction.llm_parser import parse_with_llm
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
        items = parse_with_llm(text)
        usage = TokenUsage()  # LLM token usage not implemented; default to zeros

        # Update token usage
        total_token_usage.total_tokens += usage.total_tokens
        total_token_usage.input_tokens += usage.input_tokens
        total_token_usage.output_tokens += usage.output_tokens

        # Build response
        bill_items = []
        for i in items:
            name = i.get('item_name', i.get('description', 'UNKNOWN'))
            amt = i.get('item_amount')
            rate = i.get('item_rate', 0.0)
            qty = i.get('item_quantity', 1.0)
            try:
                amt = float(amt) if amt is not None else 0.0
            except Exception:
                amt = 0.0
            try:
                rate = float(rate)
            except Exception:
                rate = 0.0
            try:
                qty = float(qty)
            except Exception:
                qty = 1.0
            bill_items.append(BillItem(item_name=name, item_amount=amt, item_rate=rate, item_quantity=qty))

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
