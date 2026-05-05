"""
OneCloud Support Chatbot API - Main Entry Point
Production-ready FastAPI backend for Hugging Face Spaces deployment
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default for Hugging Face Spaces
    port = int(os.getenv("PORT", 7860))
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
