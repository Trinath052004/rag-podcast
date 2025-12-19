import os
import uuid
import PyPDF2
from typing import List
from datetime import datetime
from app.models.pdf_processing import PDFChunk, PDFProcessingResult, PDFUploadResponse
from app.config import settings
from sentence_transformers import SentenceTransformer
import numpy as np

class PDFService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks of specified size"""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            if len(' '.join(current_chunk + [word])) <= chunk_size:
                current_chunk.append(word)
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks using sentence transformers"""
        embeddings = self.embedding_model.encode(chunks)
        return embeddings.tolist()

    def process_pdf_file(self, file_path: str, filename: str) -> PDFProcessingResult:
        """Process PDF file: extract text, chunk, and generate embeddings"""
        # Extract text from PDF
        text_content = self.extract_text_from_pdf(file_path)

        # Chunk the text
        text_chunks = self.chunk_text(text_content)

        # Generate embeddings
        embeddings = self.generate_embeddings(text_chunks)

        # Create PDFChunk objects
        chunks = []
        for i, (chunk_text, embedding) in enumerate(zip(text_chunks, embeddings)):
            chunk = PDFChunk(
                id=str(uuid.uuid4()),
                content=chunk_text,
                page_number=i // 5 + 1,  # Approximate page number
                embedding=embedding,
                metadata={
                    "source": filename,
                    "timestamp": datetime.now().isoformat(),
                    "chunk_index": i
                }
            )
            chunks.append(chunk)

        # Create processing result
        result = PDFProcessingResult(
            pdf_id=str(uuid.uuid4()),
            filename=filename,
            total_chunks=len(chunks),
            total_pages=len(text_chunks) // 5 + 1,  # Approximate page count
            status="completed",
            created_at=datetime.now(),
            chunks=chunks
        )

        return result

    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk"""
        file_id = str(uuid.uuid4())
        file_extension = filename.split('.')[-1]
        safe_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(file_path, 'wb') as file:
            file.write(file_content)

        return file_path
