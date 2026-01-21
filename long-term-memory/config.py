import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

# =========================
# OpenRouter Configuration
# =========================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct")

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found in .env")

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
# Memory Configuration
# =========================
# Short-term memory (STM)
STM_LIMIT = 10  # Keep last 10 messages in conversation

# Long-term memory (LTM)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free, fast, 384 dimensions
EMBEDDING_DIM = 384

# Semantic search
MIN_SIMILARITY = 0.7  # Minimum similarity for memory retrieval
TOP_K_MEMORIES = 5    # Retrieve top 5 most relevant memories

# Relevance weighting (similarity vs importance)
SIMILARITY_WEIGHT = 0.7  # 70% weight on semantic similarity
IMPORTANCE_WEIGHT = 0.3  # 30% weight on memory importance

# Memory extraction
EXTRACT_EVERY_N_EXCHANGES = 1  # Extract after every exchange (1 = always)

# Emphasis thresholds
HIGH_RELEVANCE_THRESHOLD = 0.85   # Highly relevant memories
MEDIUM_RELEVANCE_THRESHOLD = 0.70  # Moderately relevant memories
