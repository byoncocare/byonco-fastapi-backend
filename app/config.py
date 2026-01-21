"""
Application configuration and environment variable management
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB Configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

# CORS Origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://byoncocare.com",
    "https://www.byoncocare.com",
    "https://byonco.onrender.com",
    "https://byonco-goaj7ykq-byonco-cares-projects.vercel.app",
]
