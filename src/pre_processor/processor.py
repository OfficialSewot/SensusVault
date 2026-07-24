import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import Optional
import io
import os

class PreProcessor:
    """
    Handles multi-modal input (PDF, Images) and extracts text.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extracts text from a PDF file using PyMuPDF."""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
        return text

    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """Extracts text from an image file using Tesseract OCR."""
        try:
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception as e:
            print(f"Error extracting text from image {image_path}: {e}")
            return ""

    def process(self, file_path: str) -> str:
        """
        Routes the file to the appropriate extractor based on its extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            return self.extract_text_from_image(file_path)
        else:
            # For plain text files, just read them
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
