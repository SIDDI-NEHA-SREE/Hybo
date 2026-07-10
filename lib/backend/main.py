import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from .routes import (
    auth_routes,
    chat_routes,
    complaint_routes,
    announcement_routes,
    knowledge_routes,
    admin_routes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables (if they don't exist)
logger.info("Initializing database and tables...")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

app = FastAPI(
    title="HYBO - Hyderabad Smart City Assistant API",
    description="Backend API powering the HYBO AI RAG assistant and citizen services.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router, prefix="/api")
app.include_router(chat_routes.router, prefix="/api")
app.include_router(complaint_routes.router, prefix="/api")
app.include_router(announcement_routes.router, prefix="/api")
app.include_router(knowledge_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "HYBO Smart City API",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "api": "active"
    }
