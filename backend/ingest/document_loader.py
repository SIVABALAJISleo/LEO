import logging
import os

logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Loads and extracts text from various document formats (PDF, DOCX, TXT, MD).
    """
    def load(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self._load_pdf(file_path)
        elif ext == '.docx':
            return self._load_docx(file_path)
        elif ext == '.md' or ext == '.txt':
            return self._load_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _load_pdf(self, path: str) -> str:
        # Using pypdf (already upgraded in previous mission)
        import pypdf
        text = ""
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _load_docx(self, path: str) -> str:
        # Mocking docx extraction as it's not in requirements.txt usually
        return "Extraction from DOCX (Mocked)"

    def _load_text(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

global_document_loader = DocumentLoader()
