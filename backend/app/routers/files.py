from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.services.document import DocumentService
from app.services.ai_client import BedrockClient
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)

@router.post(
    "/analyze",
    summary="Upload and analyze a PDF, DOCX, TXT, or Image document using Textract and Bedrock"
)
async def analyze_document(
    file: UploadFile = File(...),
    action: str = Form(..., description="Action: summarize, translate, explain, or extract"),
    language: str = Form("en", description="Target language code (en, te, hi, ur)")
):
    logger.info(f"Analyzing file: {file.filename}, Action: {action}, Language: {language}")
    
    # 1. Parse File Content In-Memory
    filename = file.filename or "document.txt"
    content_type = file.content_type or ""
    
    try:
        file_bytes = await file.read()
        extracted_text = ""
        
        if filename.endswith(".pdf") or "pdf" in content_type:
            extracted_text = DocumentService.parse_pdf(file_bytes)
        elif filename.endswith(".docx") or "officedocument" in content_type:
            extracted_text = DocumentService.parse_docx(file_bytes)
        elif filename.endswith(".txt") or "text/plain" in content_type:
            extracted_text = DocumentService.parse_txt(file_bytes)
        elif filename.endswith((".png", ".jpg", ".jpeg")) or "image" in content_type:
            extracted_text = await DocumentService.parse_image_ocr(file_bytes, filename)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Supported formats: .pdf, .docx, .txt, .png, .jpg, .jpeg"
            )
            
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text found in the uploaded file"
            )
            
        # 2. Formulate Prompt based on Action
        action_prompts = {
            "summarize": f"Create a concise bulleted summary in {language} language for the following document text:\n\n{extracted_text}",
            "translate": f"Translate the following text into the {language} language:\n\n{extracted_text}",
            "explain": f"Provide a clear, detailed explanation in {language} of what this document or municipal notice means. Explain its impact on local citizens:\n\n{extracted_text}",
            "extract": f"Extract all key metadata, billing amounts, reference numbers, due dates, names, addresses, or dates in {language} from the following text:\n\n{extracted_text}"
        }
        
        prompt = action_prompts.get(
            action.lower(), 
            f"Process and explain this document content in {language}:\n\n{extracted_text}"
        )
        
        # 3. Call AI Module (Bedrock) to get response
        analysis_reply = await BedrockClient.invoke_model(
            prompt=prompt,
            preferred_lang=language
        )
        
        return {
            "filename": filename,
            "action": action,
            "extracted_text_snippet": extracted_text[:200] + "...",
            "analysis": analysis_reply
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error analyzing uploaded file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze file: {str(e)}"
        )
