"""
backend/intelligence/document_processor.py
Production-grade Document Intelligence Pipeline for LEO AI v∞.
Extracts, cleans, chunks, indexes, and summarizes PDF, DOCX, TXT, Markdown, CSV, Excel, PPTX, HTML, JSON, XML, and ZIP.
Uses pure Python standard libraries (zipfile, xml.etree, html.parser, csv, json) for ultimate portability.
"""

import os
import csv
import json
import zipfile
import re
import defusedxml.ElementTree as ET
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional

# Simple HTML Text Extractor
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self) -> str:
        return " ".join(self.text_parts)


class DocumentProcessor:
    """Document Intelligence parser and metadata generator."""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from all supported file types based on extension."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            return self._parse_txt(file_path)
        elif ext == '.md':
            return self._parse_markdown(file_path)
        elif ext == '.csv':
            return self._parse_csv(file_path)
        elif ext == '.json':
            return self._parse_json(file_path)
        elif ext == '.xml':
            return self._parse_xml(file_path)
        elif ext == '.html' or ext == '.htm':
            return self._parse_html(file_path)
        elif ext == '.docx':
            return self._parse_docx(file_path)
        elif ext == '.xlsx':
            return self._parse_xlsx(file_path)
        elif ext == '.pptx':
            return self._parse_pptx(file_path)
        elif ext == '.zip':
            return self._parse_zip(file_path)
        elif ext == '.pdf':
            return self._parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def clean_text(self, text: str) -> str:
        """Sanitize text by removing redundant whitespace, HTML residue, and non-printable characters."""
        # Replace multi-newlines
        text = re.sub(r'\n+', '\n', text)
        # Replace multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        # Strip ASCII control characters
        text = "".join(ch for ch in text if ch.isprintable() or ch in ('\n', '\r', '\t'))
        return text.strip()

    def chunk_text(self, text: str, max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Splits document text into overlapping token-aware chunks."""
        words = text.split()
        chunks = []
        
        idx = 0
        while idx < len(words):
            chunk = words[idx:idx + max_chunk_size]
            chunks.append(" ".join(chunk))
            idx += (max_chunk_size - overlap)
            
        return chunks

    def generate_metadata(self, file_path: str, raw_text: str) -> Dict[str, Any]:
        """Constructs metadata properties for document files."""
        stat = os.stat(file_path)
        words = raw_text.split()
        
        # Simple heuristic classification based on content keywords
        text_lower = raw_text.lower()
        classification = "general"
        if any(w in text_lower for w in ["def ", "class ", "import ", "function"]):
            classification = "code"
        elif any(w in text_lower for w in ["security", "vulnerability", "injection", "xss"]):
            classification = "cybersecurity"
        elif any(w in text_lower for w in ["sum", "equation", "calculate", "derivative"]):
            classification = "mathematics"

        return {
            "filename": os.path.basename(file_path),
            "file_size_bytes": stat.st_size,
            "word_count": len(words),
            "char_count": len(raw_text),
            "classification": classification,
            "is_structured": file_path.endswith(('.csv', '.json', '.xml', '.xlsx'))
        }

    # --- Parser Implementations ---

    def _parse_txt(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _parse_markdown(self, path: str) -> str:
        # Read file and strip out markdown structural syntax
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            # Strip headers, links, and bold syntax
            text = re.sub(r'#+\s+', '', text)
            text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
            text = re.sub(r'[*_`]', '', text)
            return text

    def _parse_csv(self, path: str) -> str:
        rows = []
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for r in reader:
                rows.append(" | ".join(r))
        return "\n".join(rows)

    def _parse_json(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            return json.dumps(data, indent=2)

    def _parse_xml(self, path: str) -> str:
        tree = ET.parse(path)
        root = tree.getroot()
        # Extract all text segments recursively
        texts = [elem.text.strip() for elem in root.iter() if elem.text and elem.text.strip()]
        return " ".join(texts)

    def _parse_html(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Strip script and style blocks before parsing text content
            content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            parser = HTMLTextExtractor()
            parser.feed(content)
            return parser.get_text()

    def _parse_docx(self, path: str) -> str:
        # docx is a zipped container of XML files. Main text is in word/document.xml
        texts = []
        with zipfile.ZipFile(path) as z:
            with z.open('word/document.xml') as f:
                xml_content = f.read()
                root = ET.fromstring(xml_content)
                # Word text nodes are marked by w:t namespaces
                for elem in root.iter():
                    if elem.tag.endswith('t') and elem.text:
                        texts.append(elem.text)
        return " ".join(texts)

    def _parse_xlsx(self, path: str) -> str:
        # Excel sheet data is zipped XML. Cells are indexed inside sharedStrings.xml
        texts = []
        with zipfile.ZipFile(path) as z:
            # Parse shared strings database
            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                with z.open('xl/sharedStrings.xml') as f:
                    root = ET.fromstring(f.read())
                    for elem in root.iter():
                        if elem.tag.endswith('t') and elem.text:
                            shared_strings.append(elem.text)
            
            # Parse cells in Sheet 1
            if 'xl/worksheets/sheet1.xml' in z.namelist():
                with z.open('xl/worksheets/sheet1.xml') as f:
                    root = ET.fromstring(f.read())
                    for elem in root.iter():
                        # Cell element value references shared string index
                        if elem.tag.endswith('v') and elem.text:
                            val = elem.text
                            if val.isdigit() and int(val) < len(shared_strings):
                                texts.append(shared_strings[int(val)])
                            else:
                                texts.append(val)
        return " | ".join(texts)

    def _parse_pptx(self, path: str) -> str:
        # PPTX contains slide XML structures (ppt/slides/slide1.xml, slide2.xml, etc.)
        texts = []
        with zipfile.ZipFile(path) as z:
            slide_files = [f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            # Sort slides sequentially
            slide_files.sort()
            for slide in slide_files:
                with z.open(slide) as f:
                    root = ET.fromstring(f.read())
                    # PowerPoint text element tags end with 't' (a:t)
                    for elem in root.iter():
                        if elem.tag.endswith('t') and elem.text:
                            texts.append(elem.text)
        return " ".join(texts)

    def _parse_zip(self, path: str) -> str:
        # Extract and compile all readable text documents inside zip container
        texts = []
        with zipfile.ZipFile(path) as z:
            for fileinfo in z.infolist():
                if not fileinfo.is_dir() and fileinfo.filename.endswith(('.txt', '.md', '.csv', '.xml', '.html', '.json')):
                    with z.open(fileinfo) as f:
                        texts.append(f"--- Nested File: {fileinfo.filename} ---")
                        texts.append(f.read().decode('utf-8', errors='ignore'))
        return "\n".join(texts)

    def _parse_pdf(self, path: str) -> str:
        # Simplistic binary layout scan for PDF texts (to maintain pure Python offline parser)
        # Reads raw stream segments directly from PDF file representation
        texts = []
        with open(path, 'rb') as f:
            content = f.read()
            # Extract PDF raw strings inside brackets: (Sample Text) TJ/Tj
            matches = re.findall(rb'\((.*?)\)\s*T[jJ]', content)
            for m in matches:
                try:
                    text_segment = m.decode('utf-8', errors='ignore')
                    if len(text_segment.strip()) > 1:
                        texts.append(text_segment)
                except Exception:
                    pass
        if not texts:
            # Fallback scan for raw text representations
            raw_strs = re.findall(rb'[\x20-\x7E]{4,}', content)
            texts = [s.decode('ascii', errors='ignore') for s in raw_strs if len(s) > 10]
            
        return " ".join(texts[:1000])  # limit extraction depth to protect resources
