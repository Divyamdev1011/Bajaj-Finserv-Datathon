from pydantic import BaseModel
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    amount: Optional[float]

class ExtractResponse(BaseModel):
    line_items: List[LineItem]
    calculated_total: float
    original_text_snippet: Optional[str] = None
    fraud: Optional[dict] = None
