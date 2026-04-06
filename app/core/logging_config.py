import logging
import sys

def setup_logging():
    # Create a professional logger
    logger = logging.getLogger("yms_backend")
    logger.setLevel(logging.INFO)

    # Standard format for production logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler (Docker logs collect from stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Avoid duplicate logs if handler already exists
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logging()