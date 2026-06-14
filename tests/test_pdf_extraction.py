import unittest

import fitz  # type: ignore

from services.ai_service import extract_text_from_pdf


class PDFExtractionTests(unittest.TestCase):
    def test_extract_text_from_pdf_bytes_returns_text(self):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Summary text from a generated PDF.")
        pdf_bytes = doc.tobytes()
        doc.close()

        extracted_text = extract_text_from_pdf(pdf_bytes)

        self.assertIn("Summary text", extracted_text)


if __name__ == "__main__":
    unittest.main()
