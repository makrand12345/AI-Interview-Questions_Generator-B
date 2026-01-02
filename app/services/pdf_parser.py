import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """
    Service for extracting text from PDF files with error handling.
    """
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        extracted_text = ""
        try:
            # Open PDF from memory stream
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    extracted_text += page.get_text()
            
            # Clean up whitespace and return
            return extracted_text.strip()
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {str(e)}")
            # Return empty string to allow logic to proceed without resume
            return ""

pdf_parser = PDFParser()