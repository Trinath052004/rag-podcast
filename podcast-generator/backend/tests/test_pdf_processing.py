import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from app.services.pdf_service import PDFService
from app.models.pdf_processing import PDFChunk, PDFProcessingResult
from datetime import datetime

@pytest.fixture
def pdf_service():
    return PDFService()

@pytest.fixture
def sample_pdf_content():
    return """
    Sample PDF Content

    This is a test PDF document with multiple pages.
    It contains various sections and paragraphs.

    Page 2 Content
    More text here for testing purposes.
    """

def test_pdf_text_extraction(pdf_service, sample_pdf_content):
    """Test PDF text extraction functionality"""
    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(sample_pdf_content.encode())
        temp_pdf_path = temp_pdf.name

    try:
        # Mock PyPDF2 to return our sample content
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = sample_pdf_content
            mock_pdf_reader.return_value.pages = [mock_page, mock_page]  # 2 pages

            result = pdf_service.extract_text_from_pdf(temp_pdf_path)

            assert result == f"{sample_pdf_content}\n{sample_pdf_content}\n"
            assert len(result.split('\n')) > 1
    finally:
        os.unlink(temp_pdf_path)

def test_text_chunking(pdf_service):
    """Test text chunking functionality"""
    long_text = " ".join([f"Word {i}" for i in range(100)])
    chunks = pdf_service.chunk_text(long_text, chunk_size=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert " ".join(chunks) == long_text

def test_embedding_generation(pdf_service):
    """Test embedding generation functionality"""
    sample_chunks = ["This is a test chunk", "Another test chunk"]
    embeddings = pdf_service.generate_embeddings(sample_chunks)

    assert len(embeddings) == len(sample_chunks)
    assert all(isinstance(embedding, list) for embedding in embeddings)
    assert all(len(embedding) > 0 for embedding in embeddings)

def test_pdf_processing_pipeline(pdf_service, sample_pdf_content):
    """Test complete PDF processing pipeline"""
    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(sample_pdf_content.encode())
        temp_pdf_path = temp_pdf.name

    try:
        # Mock PyPDF2 and embedding generation
        with patch('PyPDF2.PdfReader') as mock_pdf_reader, \
             patch('sentence_transformers.SentenceTransformer.encode') as mock_encode:

            # Setup PDF mock
            mock_page = MagicMock()
            mock_page.extract_text.return_value = sample_pdf_content
            mock_pdf_reader.return_value.pages = [mock_page]

            # Setup embedding mock
            mock_encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

            result = pdf_service.process_pdf_file(temp_pdf_path, "test.pdf")

            assert isinstance(result, PDFProcessingResult)
            assert result.pdf_id is not None
            assert result.filename == "test.pdf"
            assert result.total_chunks == 2
            assert result.status == "completed"
            assert len(result.chunks) == 2

            # Check chunk structure
            for chunk in result.chunks:
                assert isinstance(chunk, PDFChunk)
                assert chunk.content is not None
                assert chunk.embedding is not None
                assert chunk.metadata is not None

    finally:
        os.unlink(temp_pdf_path)

def test_file_upload_handling(pdf_service):
    """Test file upload and saving functionality"""
    test_content = b"Test PDF content"
    filename = "test_upload.pdf"

    with patch('uuid.uuid4') as mock_uuid:
        mock_uuid.return_value = "test-uuid-123"
        file_path = pdf_service.save_uploaded_file(test_content, filename)

        assert file_path.endswith("test-uuid-123.pdf")
        assert os.path.exists(file_path)

        # Clean up
        os.unlink(file_path)

def test_error_handling(pdf_service):
    """Test error handling in PDF processing"""
    # Test with invalid file path
    with pytest.raises(Exception):
        pdf_service.extract_text_from_pdf("nonexistent_file.pdf")

    # Test with empty content
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(b"")  # Empty file
        temp_pdf_path = temp_pdf.name

    try:
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_pdf_reader.return_value.pages = []
            result = pdf_service.extract_text_from_pdf(temp_pdf_path)
            assert result == ""
    finally:
        os.unlink(temp_pdf_path)
