from pypdf import PdfReader
import io
import re

class PDFParser:
    def extract_text(self, pdf_content: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Clean up whitespace
            clean_text = re.sub(r'\s+', ' ', text).strip()
            return clean_text
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

    def bifurcate_resume(self, text: str):
        """
        Simple keyword-based bifurcation to identify key sections.
        This helps the LLM focus on the right parts.
        """
        sections = {
            "skills": "",
            "experience": "",
            "projects": ""
        }
        
        # Basic split logic (can be expanded with NLP later)
        text_lower = text.lower()
        
        # Looking for common headers
        if "skills" in text_lower:
            sections["skills"] = text[text_lower.find("skills"):text_lower.find("experience")]
        
        if "experience" in text_lower:
            sections["experience"] = text[text_lower.find("experience"):]

        return sections

pdf_parser = PDFParser()