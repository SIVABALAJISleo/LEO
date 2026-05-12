import os
import csv
from typing import List, Optional
from fastapi import UploadFile, HTTPException
import io

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

class FileProcessor:
    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        """Extracts text content from various file types."""
        filename = file.filename.lower() if file.filename else ""
        content = await file.read()
        
        if filename.endswith(".csv"):
            return FileProcessor._parse_csv(content)
        elif filename.endswith(".pdf"):
            return FileProcessor._parse_pdf(content)
        elif filename.endswith(".docx"):
            return FileProcessor._parse_docx(content)
        elif filename.endswith(".txt"):
            return content.decode("utf-8")
        else:
            # Fallback to direct decode for unknown text formats
            try:
                return content.decode("utf-8")
            except:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}")

    @staticmethod
    def _parse_csv(content: bytes) -> str:
        """Converts CSV rows into a single string for RAG or batch processing."""
        decoded = content.decode("utf-8")
        reader = csv.reader(io.StringIO(decoded))
        return "\n".join([",".join(row) for row in reader])

    @staticmethod
    def _parse_pdf(content: bytes) -> str:
        """Extracts text from PDF buffers."""
        if not HAS_PDF:
             return "PDF parsing currently unavailable (missing PyPDF2 dependency)."
        
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def _parse_docx(content: bytes) -> str:
        """Extracts text from DOCX buffers."""
        if not HAS_DOCX:
            return "DOCX parsing currently unavailable (missing python-docx dependency)."
        
        try:
            doc = Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")

file_processor = FileProcessor()
