import re
from fastapi import HTTPException, status
from typing import Optional

def validate_pdf_file(filename: str):
    """Validate that the uploaded file is a PDF"""
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024):
    """Validate file size (default max: 10MB)"""
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {max_size / (1024 * 1024)}MB"
        )

def validate_pdf_id(pdf_id: str):
    """Validate PDF ID format"""
    if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', pdf_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF ID format"
        )

def validate_text_content(content: str, min_length: int = 10, max_length: int = 10000):
    """Validate text content length"""
    if len(content) < min_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content too short. Minimum {min_length} characters required"
        )
    if len(content) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content too long. Maximum {max_length} characters allowed"
        )
