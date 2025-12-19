from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.pdf_service import PDFService
from app.models.pdf_processing import PDFUploadResponse
from typing import Optional

router = APIRouter()

pdf_service = PDFService()

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    try:
        # Save the uploaded file
        file_path = pdf_service.save_uploaded_file(await file.read(), file.filename)

        # Process the PDF file
        result = pdf_service.process_pdf_file(file_path, file.filename)

        return PDFUploadResponse(
            pdf_id=result.pdf_id,
            filename=result.filename,
            status="success",
            message=f"PDF processed successfully. Generated {result.total_chunks} chunks."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

@router.get("/status/{pdf_id}")
async def get_pdf_status(pdf_id: str):
    """Get processing status of a PDF"""
    # In a real implementation, this would check a database or cache
    return {"pdf_id": pdf_id, "status": "completed", "message": "PDF processing completed successfully"}

@router.get("/chunks/{pdf_id}")
async def get_pdf_chunks(pdf_id: str, limit: Optional[int] = 10, offset: Optional[int] = 0):
    """Get chunks for a processed PDF"""
    # In a real implementation, this would retrieve from database or cache
    sample_chunks = [
        {"id": "1", "content": "Sample chunk content...", "page_number": 1},
        {"id": "2", "content": "Another sample chunk...", "page_number": 1}
    ]

    return {
        "pdf_id": pdf_id,
        "chunks": sample_chunks[offset:offset+limit],
        "total_chunks": len(sample_chunks),
        "limit": limit,
        "offset": offset
    }
