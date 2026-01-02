from pypdf import PdfReader
import io

class PDFParser:
    def extract_text(self, pdf_content: bytes) -> str:
        try:
            # Create a file-like object from the bytes
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

pdf_parser = PDFParser()