"""
Configuration for Discord Class Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

# Paths
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_BOT_PREFIX = "!"

# OpenRouter Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "openai/text-embedding-3-small")

# RAG Configuration
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 50  # tokens
TOP_K = 10  # số lượng kết quả retrieval
SIMILARITY_THRESHOLD = 0.25  # ngưỡng similarity tối thiểu
MAX_CONTEXT_LENGTH = 4000  # characters

# Bot Configuration
MAX_RESPONSE_TOKENS = 500
TEMPERATURE = 0.3
BOT_LANGUAGE = "vi"  # Vietnamese

# Channel Configuration
ALLOWED_CHANNELS = os.getenv("ALLOWED_CHANNELS", "general").split(",")

# Rate Limiting
RATE_LIMIT_PER_USER = 5  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "bot.log"
