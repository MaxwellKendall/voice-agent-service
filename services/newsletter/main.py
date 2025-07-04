"""Main entry point for the AI Recipe Agent API."""

import uvicorn
import logging
from app.api import app
from app.config import HOST, PORT, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting AI Recipe Agent API on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    
    uvicorn.run(
        "app.api:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    ) 