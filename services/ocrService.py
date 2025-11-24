import io
import pdfplumber

class OCRService:

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> str:
        # Verify it's a PDF
        if file_bytes[:4] != b"%PDF":
            raise ValueError("Only PDF files are supported. Expected PDF format.")
        
        text = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
