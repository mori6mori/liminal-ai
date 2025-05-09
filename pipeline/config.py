"""
config.py - Configuration settings for the pipeline
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Default model

# Chunker configuration
MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Check if API key is available
def validate_api_key():
    """Validate that required API keys are present"""
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in a .env file or export it in your shell.")
        return False
    return True 