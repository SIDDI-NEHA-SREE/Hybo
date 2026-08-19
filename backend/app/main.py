from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import settings
from app.utils.logger import logger
from app.routers import chat, voice, files, auth, knowledge

app = FastAPI(
    title=settings.APP_NAME,
    description="HYBO Assistant API - AI-powered Smart City Assistant for Hyderabad and Telangana",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler for Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request validation failed for path {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": exc.errors()
        }
    )

# Include Routers
app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(files.router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health")
async def health_check():
    logger.info("Health check endpoint hit")
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "debug_mode": settings.DEBUG
    }
