from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PDFChunk(BaseModel):
    id: str
    content: str
    page_number: int
    embedding: Optional[List[float]] = None
    metadata: dict

    class Config:
        from_attributes = True

class PDFProcessingResult(BaseModel):
    pdf_id: str
    filename: str
    total_chunks: int
    total_pages: int
    status: str
    created_at: datetime
    chunks: List[PDFChunk]

class PDFUploadResponse(BaseModel):
    pdf_id: str
    filename: str
    status: str
    message: str
