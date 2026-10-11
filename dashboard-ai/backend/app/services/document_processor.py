"""
Document processing service for text extraction and chunking.
Supports PDF, DOCX, TXT, MD, and CSV formats.
"""
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import tiktoken

# Document readers
import PyPDF2
from docx import Document as DocxDocument
import pandas as pd
import markdown

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a chunk of text from a document."""
    
    def __init__(
        self,
        text: str,
        chunk_index: int,
        page_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.metadata = metadata or {}
        self.char_count = len(text)


class DocumentProcessor:
    """Service for extracting and chunking document text."""
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 75):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target tokens per chunk (default: 600)
            chunk_overlap: Token overlap between chunks (default: 75)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from a document.
        
        Args:
            file_path: Path to the document
            file_type: File type (pdf, docx, txt, md, csv)
            
        Returns:
            Extracted text
        """
        try:
            if file_type == "pdf":
                return self._extract_pdf(file_path)
            elif file_type == "docx":
                return self._extract_docx(file_path)
            elif file_type == "txt":
                return self._extract_txt(file_path)
            elif file_type == "md":
                return self._extract_markdown(file_path)
            elif file_type == "csv":
                return self._extract_csv(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Add page marker for tracking
                    text += f"\n[PAGE {page_num + 1}]\n{page_text}\n"
        return text
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = DocxDocument(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    
    def _extract_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            md_text = file.read()
            # Convert markdown to plain text (strip formatting)
            html = markdown.markdown(md_text)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            return text
    
    def _extract_csv(self, file_path: str) -> str:
        """Extract text from CSV file."""
        df = pd.read_csv(file_path)
        # Convert DataFrame to readable text
        text = f"CSV Data ({len(df)} rows, {len(df.columns)} columns)\n\n"
        text += "Columns: " + ", ".join(df.columns.tolist()) + "\n\n"
        text += df.to_string(index=False)
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        return text.strip()
    
    def chunk_text(self, text: str, file_type: str = "txt") -> List[DocumentChunk]:
        """
        Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            file_type: Original file type for context
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Extract page markers from PDF text
        page_pattern = r'\[PAGE (\d+)\]'
        pages = re.split(page_pattern, text)
        
        # If PDF with page markers
        if len(pages) > 1:
            chunks = self._chunk_with_pages(pages)
        else:
            # Regular chunking without page tracking
            chunks = self._chunk_by_tokens(text)
        
        return chunks
    
    def _chunk_with_pages(self, pages: List[str]) -> List[DocumentChunk]:
        """Chunk PDF text while preserving page numbers."""
        chunks = []
        chunk_index = 0
        
        for i in range(1, len(pages), 2):
            if i >= len(pages):
                break
                
            page_num = int(pages[i])
            page_text = pages[i + 1] if i + 1 < len(pages) else ""
            
            if not page_text.strip():
                continue
            
            # Chunk this page's text
            page_chunks = self._chunk_by_tokens(page_text)
            
            # Assign page number to chunks
            for chunk in page_chunks:
                chunks.append(DocumentChunk(
                    text=chunk.text,
                    chunk_index=chunk_index,
                    page_number=page_num
                ))
                chunk_index += 1
        
        return chunks
    
    def _chunk_by_tokens(self, text: str) -> List[DocumentChunk]:
        """Chunk text by token count with overlap."""
        chunks = []
        tokens = self.tokenizer.encode(text)
        
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            # Get chunk tokens
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunks.append(DocumentChunk(
                text=chunk_text,
                chunk_index=chunk_index
            ))
            
            chunk_index += 1
            
            # Move start position with overlap
            start = start + self.chunk_size - self.chunk_overlap
            
            # Prevent infinite loop
            if start >= len(tokens):
                break
        
        return chunks
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
            
        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))


# Singleton instance
document_processor = DocumentProcessor()
