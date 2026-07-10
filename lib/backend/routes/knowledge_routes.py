import io
import json
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..auth import get_current_user, require_admin, require_official
from ..rag import rag_manager

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    
    if ext in ["txt", "md"]:
        return file_bytes.decode("utf-8", errors="ignore")
        
    elif ext == "pdf":
        try:
            from pypdf import PdfReader
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text_content = page.extract_text()
                if text_content:
                    text += text_content + "\n"
            return text
        except ImportError:
            logger.error("pypdf is not installed.")
            raise HTTPException(status_code=500, detail="PDF parser dependency is missing.")
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF file: {str(e)}")
            
    elif ext == "docx":
        try:
            import docx
            doc_file = io.BytesIO(file_bytes)
            doc = docx.Document(doc_file)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            logger.error("python-docx is not installed.")
            raise HTTPException(status_code=500, detail="DOCX parser dependency is missing.")
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse DOCX file: {str(e)}")
            
    elif ext == "csv":
        try:
            import csv
            text_stream = io.StringIO(file_bytes.decode("utf-8", errors="ignore"))
            reader = csv.reader(text_stream)
            rows = []
            for r in reader:
                rows.append(", ".join(r))
            return "\n".join(rows)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")
            
    elif ext == "json":
        try:
            data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            if isinstance(data, dict) or isinstance(data, list):
                return json.dumps(data, indent=2, ensure_ascii=False)
            return str(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse JSON file: {str(e)}")
            
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: {ext}"
        )

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    current_user: User = Depends(require_official)
):
    try:
        content = await file.read()
        text = extract_text(content, file.filename)
        
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extracted text is empty. The document may be empty or contain non-extractable text (e.g. scanned image)."
            )

        # Add to vector database
        rag_manager.add_documents(
            text=text,
            source=file.filename,
            title=title,
            category=category
        )
        
        return {
            "filename": file.filename,
            "title": title,
            "category": category,
            "status": "success",
            "message": f"Successfully chunked and embedded document: {file.filename}"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/status")
def get_status(current_user: User = Depends(get_current_user)):
    return {
        "index_size": len(rag_manager.chunks),
        "embedding_dimension": rag_manager.dimension,
        "is_using_gemini": bool(settings.GEMINI_API_KEY)
    }

@router.post("/clear")
def clear_knowledge(current_user: User = Depends(require_admin)):
    rag_manager.clear_index()
    return {"message": "Knowledge base index cleared successfully."}
