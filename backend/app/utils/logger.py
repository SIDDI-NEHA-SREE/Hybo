import logging
import sys
from app.config import settings

def setup_logger():
    logger = logging.getLogger(settings.APP_NAME)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Check if handler already exists (prevents duplicate logs)
    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()
