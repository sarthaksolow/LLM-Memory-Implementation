# LLM Memory Practice - Short-term & Long-term Memory

This project implements different memory strategies for LLMs using LangGraph and PostgreSQL with vector embeddings.

## Project Structure

```
llm memory/
├── docker-compose.yml          # PostgreSQL with pgvector extension
├── .env                        # Environment variables (API keys, DB config)
├── .gitignore
├── short-term-memory/
│   ├── trimming/               # ✅ Strategy 1: Message Trimming
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── requirements.txt
│   ├── summary/                # ✅ Strategy 2: Conversation Summary
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── requirements.txt
│   └── user-progress/          # 🔜 Strategy 3: User Progress Tracking
│       └── (to be implemented)
└── long-term-memory/           # ✅ Long-term Memory with Semantic Search
    ├── main.py                 # LangGraph implementation
    ├── config.py               # Configuration
    ├── database.py             # PostgreSQL + pgvector operations
    ├── embeddings.py           # Embedding generation (sentence-transformers)
    ├── memory_extractor.py     # LLM-based memory extraction
    ├── memory_manager.py       # Memory lifecycle management
    ├── context_builder.py      # Context window assembly
    └── requirements.txt
```

---

## Setup Instructions

### 1. Configure Environment Variables

Edit the `.env` file and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_actual_api_key_here
MODEL_NAME=meta-llama/llama-3.1-8b-instruct
```

### 2. Start PostgreSQL with pgvector

**IMPORTANT:** We now use `ankane/pgvector` image for semantic search support!

```bash
# Navigate to project folder
cd "D:\llm memory"

# Stop old container if running
docker-compose down -v

# Start PostgreSQL container with pgvector
docker-compose up -d

# Check if container is running
docker ps

# View logs (optional)
docker logs llm_memory_postgres
```

### 3. Install Python Dependencies

Each strategy has its own `requirements.txt`:

```bash
# For long-term memory (recommended to start here)
cd "long-term-memory"
pip install -r requirements.txt

# For trimming strategy
cd "short-term-memory\trimming"
pip install -r requirements.txt

# For summary strategy
cd "short-term-memory\summary"
pip install -r requirements.txt
```

**Note:** Long-term memory requires additional packages:
- `sentence-transformers` - For embedding generation (~400MB download first time)
- `pgvector` - PostgreSQL vector extension support
- `numpy` - Numerical operations

**Recommended:** Use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

---

## Long-term Memory (LTM) - The Main Implementation 🧠

**How it works:**
A complete LTM system with semantic search, memory extraction, and intelligent retrieval.

### Architecture Flow:
```
User Input
    ↓
1. LTM Search (Semantic) → Retrieve relevant memories
    ↓
2. STM Retrieval → Get recent conversation
    ↓
3. Context Assembly → Combine LTM + STM + System Prompt
    ↓
4. LLM Generation → Generate response
    ↓
5. Memory Extraction → Store new important info in LTM
```

### The 4 Steps of LTM:

#### 1. **CREATE** - Memory Extraction
- Uses LLM to analyze conversations
- Extracts only important information worth remembering
- Categorizes: `personal_info`, `preference`, `fact`, `decision`, `goal`
- Assigns importance score (1-10)

**Example:**
```
User: "My name is Sarah and I'm building a weather app"
↓
Extracted Memory:
{
  "content": "User's name is Sarah. Working on weather app project.",
  "memory_type": "personal_info",
  "importance": 8
}
```

#### 2. **STORE** - Save with Embeddings
- Converts memory text to 384-dimensional vector embedding
- Stores in PostgreSQL with pgvector extension
- Enables semantic search (not just keyword matching)

**Database Schema:**
```sql
ltm_memories
├── id (primary key)
├── user_id (indexed)
├── content (text)
├── memory_type (personal_info/preference/fact/decision/goal)
├── importance (1-10)
├── embedding (VECTOR(384)) -- Semantic embedding
├── created_at
├── last_accessed
└── access_count
```

#### 3. **SEARCH** - Semantic Retrieval
- Generates embedding for user's current query
- Uses cosine similarity to find relevant memories
- Returns top K memories above similarity threshold

**Example:**
```
Query: "What was I working on?"
↓
Embedding: [0.23, -0.45, 0.67, ...]
↓
Search LTM using cosine similarity
↓
Found: "User's name is Sarah. Working on weather app project."
Similarity: 0.89
```

#### 4. **RETRIEVE** - Relevance Weighting
- Combines similarity score + importance
- Formula: `relevance = (similarity × 0.7) + (importance/10 × 0.3)`
- Updates access tracking (count, last_accessed)

### Run Long-term Memory:

```bash
cd "long-term-memory"
python main.py
```

### Commands:
- Type your message to chat
- `memories` - View all stored memories
- `stats` - View memory statistics
- `clear` - Clear all data (STM + LTM)
- `quit` - Exit

### Example Session:

```
You: Hi, my name is Alex and I love Python programming

🔍 Searching long-term memories...
   No relevant memories found

🧠 Extracting memories...
   ✅ Memory created: [personal_info] User's name is Alex. Enjoys Python programming.
   Importance: 8/10

🤖 Assistant: Hello Alex! It's great to meet you! Python is an excellent language...

---

(Later in conversation...)

You: What programming languages do I like?

🔍 Searching long-term memories...
   ✅ Found 1 relevant memories:
   1. [personal_info] User's name is Alex. Enjoys Python programming.
      Relevance: 0.91 (similarity: 0.94, importance: 8/10)

🤖 Assistant: Based on what you've told me, you love Python programming!
```

### Configuration Options:

```python
# config.py - Customize these settings

STM_LIMIT = 10                    # Recent messages to keep
TOP_K_MEMORIES = 5                # Max memories to retrieve
MIN_SIMILARITY = 0.7              # Minimum similarity threshold

SIMILARITY_WEIGHT = 0.7           # Weight for semantic similarity
IMPORTANCE_WEIGHT = 0.3           # Weight for memory importance

HIGH_RELEVANCE_THRESHOLD = 0.85   # High emphasis threshold
MEDIUM_RELEVANCE_THRESHOLD = 0.70 # Medium emphasis threshold
```

### Key Features:
- ✅ **Semantic search** - Finds relevant memories by meaning, not keywords
- ✅ **Smart extraction** - LLM decides what's worth remembering
- ✅ **Relevance weighting** - Balances similarity and importance
- ✅ **Access tracking** - Tracks which memories are most useful
- ✅ **Multi-user support** - Each user has their own memories
- ✅ **Persistent storage** - Memories survive across sessions

---

## Short-term Memory Strategies

### Strategy 1: Trimming ✂️

**How it works:**
- Keeps only the last N messages (default: 10)
- Automatically deletes older messages from PostgreSQL
- Simple sliding window approach

**Database Schema:**
```
messages_trimming
├── id (primary key)
├── session_id (indexed)
├── role (user/assistant)
├── content (text)
└── timestamp
```

**Run:**
```bash
cd "short-term-memory\trimming"
python main.py
```

**Best for:** Short, casual conversations where old context isn't needed

---

### Strategy 2: Summary 🧠

**How it works:**
- Keeps only recent N messages (default: 10) in raw form
- When limit exceeded, summarizes oldest K messages (default: 5)
- Stores summary separately and deletes summarized messages
- Summary evolves as conversation grows

**Database Schema:**
```
messages_summary
├── id, session_id, role, content, timestamp

conversation_summary
├── session_id (primary key)
├── summary (text)
└── updated_at
```

**Run:**
```bash
cd "short-term-memory\summary"
python main.py
```

**Best for:** Long conversations where historical context matters

---

## Comparison: All Memory Strategies

| Aspect | Trimming ✂️ | Summary 🧠 | Long-term Memory 💾 |
|--------|------------|-----------|-------------------|
| **Storage** | PostgreSQL | PostgreSQL | PostgreSQL + Vectors |
| **Old messages** | Deleted | Summarized | Extracted as memories |
| **Context retention** | Lost | Condensed | Semantically searchable |
| **Token usage** | Low | Medium | Medium-High |
| **Information loss** | High | Low | Very Low |
| **Setup complexity** | Simple | Moderate | Complex |
| **Cross-session memory** | No | No | **Yes** |
| **Semantic search** | No | No | **Yes** |
| **Best for** | Casual chats | Long conversations | Personal assistants |

---

## Docker Management

### Start PostgreSQL:
```bash
docker-compose up -d
```

### Stop PostgreSQL:
```bash
docker-compose down
```

### Stop and remove all data:
```bash
docker-compose down -v
```

### View logs:
```bash
docker logs llm_memory_postgres
```

### Access PostgreSQL CLI:
```bash
docker exec -it llm_memory_postgres psql -U llm_user -d llm_memory_db
```

### Useful SQL queries:
```sql
-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- View long-term memories
SELECT id, user_id, memory_type, importance, content, access_count 
FROM ltm_memories 
ORDER BY created_at DESC;

-- View STM messages
SELECT * FROM stm_messages ORDER BY timestamp DESC LIMIT 20;

-- Count memories by type
SELECT memory_type, COUNT(*) 
FROM ltm_memories 
GROUP BY memory_type;

-- Most accessed memories
SELECT content, access_count, last_accessed 
FROM ltm_memories 
ORDER BY access_count DESC 
LIMIT 10;
```

---

## How It All Works Together

### Connection Flow (Python → Docker PostgreSQL):

```
Python Script (main.py)
    ↓
Connects to: localhost:5432
    ↓
Docker Port Mapping (5432:5432)
    ↓
Container Port 5432
    ↓
PostgreSQL with pgvector
```

Your Python code connects to `localhost:5432`, and Docker transparently forwards it to the container!

### Memory Lifecycle:

```
1. User sends message
    ↓
2. Search LTM for relevant memories (semantic search)
    ↓
3. Retrieve recent STM messages
    ↓
4. Build context: System + LTM + STM
    ↓
5. Send to LLM
    ↓
6. Get response
    ↓
7. Extract new memories (if important info)
    ↓
8. Store in LTM with embeddings
    ↓
9. Store message in STM
```

---

## Troubleshooting

### PostgreSQL connection error:
- **Check Docker:** `docker ps`
- **Verify pgvector image:** Should show `ankane/pgvector`
- **Check port 5432:** `netstat -ano | findstr :5432`
- **Restart:** `docker-compose down && docker-compose up -d`

### Embedding model download issues:
- First run downloads `all-MiniLM-L6-v2` (~400MB)
- Requires internet connection
- Downloads to `~/.cache/torch/sentence_transformers/`

### pgvector extension error:
- Make sure you're using `ankane/pgvector` image (not `postgres:15-alpine`)
- Run: `docker-compose down -v && docker-compose up -d`
- Check extension: `docker exec -it llm_memory_postgres psql -U llm_user -d llm_memory_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"`

### Import errors:
- Install all requirements: `pip install -r requirements.txt`
- Activate virtual environment if using one
- For `pgvector` package issues, try: `pip install pgvector --upgrade`

---

## Learning Outcomes

By completing this project, you'll understand:
- ✅ Short-term vs Long-term memory in LLMs
- ✅ Semantic search with vector embeddings
- ✅ PostgreSQL pgvector extension
- ✅ LLM-based information extraction
- ✅ Context window management
- ✅ LangGraph for stateful AI applications
- ✅ Docker for development databases
- ✅ Memory relevance weighting and retrieval

---

## Next Steps

1. ✅ Test trimming strategy
2. ✅ Test summary strategy
3. ✅ **Test long-term memory (START HERE!)**
4. 🔜 Implement user-progress tracking
5. 🔜 Add memory consolidation (merge similar memories)
6. 🔜 Implement memory decay/forgetting
7. 🔜 Add importance auto-adjustment based on access patterns

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenRouter API](https://openrouter.ai/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

---

## License

This is a practice project for learning purposes. Feel free to modify and experiment!

**Happy Learning! 🚀🧠**
