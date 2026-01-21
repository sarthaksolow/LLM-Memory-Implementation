# LLM Memory Practice - Short-term Memory

This project implements three different short-term memory strategies for LLMs using LangGraph and PostgreSQL.

## Project Structure

```
llm memory/
├── docker-compose.yml          # PostgreSQL setup
├── .env                        # Environment variables (API keys, DB config)
├── .gitignore
└── short-term-memory/
    ├── trimming/               # ✅ Strategy 1: Message Trimming
    │   ├── main.py
    │   ├── config.py
    │   ├── database.py
    │   └── requirements.txt
    ├── summary/                # ✅ Strategy 2: Conversation Summary
    │   ├── main.py
    │   ├── config.py
    │   ├── database.py
    │   └── requirements.txt
    └── user-progress/          # 🔜 Strategy 3: User Progress Tracking
        └── (to be implemented)
```

## Setup Instructions

### 1. Configure Environment Variables

Edit the `.env` file and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_actual_api_key_here
MODEL_NAME=meta-llama/llama-3.1-8b-instruct
```

**Note:** For the summary strategy, do NOT use `:free` models as they may not support the summarization quality needed.

### 2. Start PostgreSQL with Docker

```bash
# Navigate to project folder
cd "D:\llm memory"

# Start PostgreSQL container
docker-compose up -d

# Check if container is running
docker ps

# View logs (optional)
docker logs llm_memory_postgres
```

### 3. Install Python Dependencies

Each strategy has its own `requirements.txt`. Install for the strategy you want to test:

```bash
# For trimming strategy
cd "short-term-memory\trimming"
pip install -r requirements.txt

# For summary strategy
cd "short-term-memory\summary"
pip install -r requirements.txt
```

**Recommended:** Use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

---

## Strategy 1: Trimming ✂️

**How it works:**
- Keeps only the last N messages (default: 10)
- Automatically deletes older messages from PostgreSQL
- Simple sliding window approach
- **Best for:** Short, casual conversations where old context isn't needed

### Database Schema:
```
messages_trimming
├── id (primary key)
├── session_id (indexed)
├── role (user/assistant)
├── content (text)
└── timestamp
```

### Run:
```bash
cd "short-term-memory\trimming"
python main.py
```

### Commands:
- Type your message to chat
- `stats` - View current message count
- `clear` - Clear chat history
- `quit` - Exit

### Example Flow:
```
Messages 1-10: Stored normally
Message 11: Triggers trimming
  ↓
Message 1 deleted (oldest)
Messages 2-11 remain (10 total)
```

### Key Features:
- Automatic trimming after each user message
- Session-based conversation tracking
- Configurable message limit (`MAX_MESSAGES = 10`)

---

## Strategy 2: Summary 🧠

**How it works:**
- Keeps only recent N messages (default: 10) in raw form
- When limit is exceeded, summarizes oldest K messages (default: 5)
- Stores summary separately and deletes summarized messages
- Summary evolves as conversation grows (merges with new summaries)
- **Best for:** Long conversations where historical context matters

### Database Schema:
```
messages_summary
├── id (primary key)
├── session_id (indexed)
├── role (user/assistant)
├── content (text)
└── timestamp

conversation_summary
├── session_id (primary key)
├── summary (text)
└── updated_at
```

### Run:
```bash
cd "short-term-memory\summary"
python main.py
```

### Commands:
- Type your message to chat
- `quit` - Exit

### Example Flow:
```
Messages 1-10: Stored as raw messages
  ↓
Message 11 arrives (exceeds STM_LIMIT=10)
  ↓
Summarize messages 1-5 using LLM
  ↓
Store summary: "User discussed X, Y, Z..."
  ↓
Delete messages 1-5
  ↓
Result: 6 raw messages + 1 summary

Messages 12-15: Stored normally
  ↓
Message 16 arrives (exceeds limit again)
  ↓
Summarize messages 6-10
  ↓
UPDATE existing summary (merge with new info)
  ↓
Delete messages 6-10
  ↓
Result: 6 raw messages + updated summary
```

### Context Sent to LLM:
```python
1. System message
2. Conversation summary (if exists)
3. Recent raw messages (last 6-10)
```

### Key Features:
- **No information loss** - Old messages condensed, not deleted
- **Evolving summaries** - Summary updates as conversation grows
- **Smart chunking** - Summarizes 5 messages at a time
- **Efficient token usage** - Summary + recent messages only
- Configurable limits (`STM_LIMIT = 10`, `SUMMARY_CHUNK = 5`)

### Configuration:
```python
STM_LIMIT = 10       # Max raw messages to keep
SUMMARY_CHUNK = 5    # How many messages to summarize at once
```

---

## Strategy 3: User Progress Tracking 📊

**Status:** 🔜 To be implemented

**Planned features:**
- Track user metadata and conversation state
- Store user preferences, goals, topics discussed
- Monitor conversation progress (e.g., "completed onboarding", "discussed topic X")
- Persistent user profile across sessions

---

## Comparison: Trimming vs Summary

| Aspect | Trimming ✂️ | Summary 🧠 |
|--------|------------|-----------|
| **Old messages** | Deleted forever | Condensed into summary |
| **Context retention** | Lost after deletion | Preserved in summary |
| **Token usage** | Lower (fewer messages) | Medium (summary + recent) |
| **Information loss** | High | Low |
| **Setup complexity** | Simple | Moderate |
| **LLM calls** | 1 per message | 2 per message (when summarizing) |
| **Best for** | Short, casual chats | Long, context-heavy conversations |
| **Database tables** | 1 (messages) | 2 (messages + summary) |

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
-- View all messages in trimming strategy
SELECT * FROM messages_trimming ORDER BY timestamp;

-- View all messages in summary strategy
SELECT * FROM messages_summary ORDER BY timestamp;

-- View summaries
SELECT * FROM conversation_summary;

-- Count messages per session
SELECT session_id, COUNT(*) FROM messages_trimming GROUP BY session_id;
```

---

## Troubleshooting

### PostgreSQL connection error:
- **Check Docker is running:** `docker ps`
- **Verify container is up:** Should see `llm_memory_postgres`
- **Check port 5432:** Make sure it's not in use by another service
- **Restart container:** `docker-compose down && docker-compose up -d`

### OpenRouter API error:
- Verify your API key in `.env`
- Check if you have credits in OpenRouter
- For summary strategy, avoid `:free` models (they may not summarize well)

### Import errors:
- Make sure you've installed all requirements: `pip install -r requirements.txt`
- Activate virtual environment if using one: `venv\Scripts\activate`

### Database table not found:
- Tables are created automatically on first run
- If issues persist, restart: `docker-compose down -v && docker-compose up -d`

---

## How Docker Connection Works

**Port Mapping:**
```yaml
ports:
  - "5432:5432"
```

This maps:
- **Host (your computer):** Port 5432
- **Container:** Port 5432

**Connection flow:**
```
Python script
    ↓
Connects to localhost:5432
    ↓
Docker intercepts (port mapping)
    ↓
Forwards to container:5432
    ↓
PostgreSQL in container receives connection
```

Your Python code thinks it's connecting to a local PostgreSQL, but Docker transparently forwards it to the container!

---

## Next Steps

1. ✅ Test the trimming strategy
2. ✅ Test the summary strategy
3. 🔜 Implement user-progress tracking strategy
4. 🔜 Explore long-term memory (separate project)
5. 🔜 Compare performance and token usage across strategies

---

## Learning Outcomes

By completing this project, you'll understand:
- ✅ How LLMs manage conversation context
- ✅ Trade-offs between different memory strategies
- ✅ PostgreSQL with Docker for quick development
- ✅ LangGraph for building stateful AI applications
- ✅ SQLAlchemy ORM for database operations
- ✅ How to design scalable memory systems

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenRouter API](https://openrouter.ai/docs)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

## License

This is a practice project for learning purposes. Feel free to modify and experiment!

**Happy Learning! 🚀**
