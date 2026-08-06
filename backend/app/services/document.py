import io
import boto3
from pypdf import PdfReader
from docx import Document
from app.config import settings
from app.utils.logger import logger

class DocumentService:
    _textract_client = None

    @classmethod
    def _get_textract(cls):
        if not settings.is_aws_configured:
            logger.info("AWS credentials not configured. Textract client is disabled.")
            return None
        if cls._textract_client is None:
            try:
                cls._textract_client = boto3.client(
                    "textract",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            except Exception as e:
                logger.error(f"Failed to load AWS Textract client: {str(e)}")
                cls._textract_client = None
        return cls._textract_client

    @classmethod
    def parse_pdf(cls, file_bytes: bytes) -> str:
        """
        Parses text from a PDF file stream in-memory.
        """
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF file: {str(e)}")
            raise ValueError("Invalid PDF format or unreadable content")

    @classmethod
    def parse_docx(cls, file_bytes: bytes) -> str:
        """
        Parses text from a Word (.docx) file stream in-memory.
        """
        try:
            doc = Document(io.BytesIO(file_bytes))
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise ValueError("Invalid DOCX format or unreadable content")

    @classmethod
    def parse_txt(cls, file_bytes: bytes) -> str:
        """
        Parses text from a plain TXT file.
        """
        try:
            return file_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("latin-1").strip()
            except Exception as e:
                logger.error(f"Error decoding text file: {str(e)}")
                raise ValueError("Could not decode plain text content")

    @classmethod
    async def parse_image_ocr(cls, file_bytes: bytes, filename: str) -> str:
        """
        Sends image bytes to AWS Textract for OCR text block extraction.
        Fallbacks to mock OCR text on mock credentials.
        """
        textract = cls._get_textract()
        if textract is None:
            logger.info("Textract offline mode: Simulating OCR extraction.")
            return cls._simulate_ocr_fallback(filename)

        try:
            # Synchronous document text detection (fits Free Tier single page limits)
            response = textract.detect_document_text(
                Document={'Bytes': file_bytes}
            )
            
            blocks = response.get("Blocks", [])
            extracted_lines = []
            for block in blocks:
                if block.get("BlockType") == "LINE":
                    extracted_lines.append(block.get("Text", ""))
                    
            return "\n".join(extracted_lines)
            
        except Exception as e:
            logger.error(f"AWS Textract OCR failed: {str(e)}. Returning mock OCR.")
            return cls._simulate_ocr_fallback(filename)

    @staticmethod
    def _simulate_ocr_fallback(filename: str) -> str:
        """
        Generates simulated high-quality OCR text for testing Telangana/Hyderabad uploads offline.
        """
        fn_lower = filename.lower()
        if "bill" in fn_lower:
            return (
                "--- MOCK OCR: TSSPDCL Electricity Bill ---\n"
                "Southern Power Distribution Company of Telangana Limited\n"
                "Consumer No: 102938475\n"
                "Name: M. Srinivas\n"
                "Address: Banjara Hills, Road No. 12, Hyderabad - 500034\n"
                "Billing Month: July 2026\n"
                "Total Amount Due: INR 4,320.00\n"
                "Due Date: 15-08-2026\n"
            )
        elif "notice" in fn_lower or "go" in fn_lower:
            return (
                "--- MOCK OCR: GOVERNMENT OF TELANGANA NOTICE ---\n"
                "Municipal Administration & Urban Development Department\n"
                "GO.Ms.No. 42 | Dated: 10-06-2026\n"
                "Subject: Allocation of budgets for flyover developmental works under GHMC limits.\n"
                "Sanctioned Amount: Rs. 150 Crores\n"
                "Officer: Principal Secretary, Telangana Gov.\n"
            )
        else:
            return (
                f"--- MOCK OCR: {filename} ---\n"
                "Government of Telangana\n"
                "Greater Hyderabad Municipal Corporation (GHMC)\n"
                "Verified Document Details\n"
                "Office Location: Hyderabad, India\n"
            )
