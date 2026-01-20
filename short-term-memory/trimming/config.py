import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# =========================
# OpenRouter Configuration
# =========================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "meta-llama/llama-3.1-8b-instruct"
)

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found in environment")

if ":free" in MODEL_NAME:
    raise ValueError(
        "❌ Invalid MODEL_NAME: ':free' is not supported by OpenRouter API"
    )

# =========================
# PostgreSQL Configuration
# =========================
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "llm_memory_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "llm_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "llm_password")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# =========================
# Short-Term Memory Config
# =========================
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", 10))
