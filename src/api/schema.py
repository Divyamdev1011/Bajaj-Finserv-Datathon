from pydantic import BaseModel
from typing import List

class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float

class PageLineItems(BaseModel):
    page_no: str
    page_type: str
    bill_items: List[BillItem]

class TokenUsage(BaseModel):
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

class DataModel(BaseModel):
    pagewise_line_items: List[PageLineItems]
    total_item_count: int

class ReportResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: DataModel
