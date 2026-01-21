# Long-term Memory (LTM) Setup Guide

## Quick Start (5 Minutes)

### Step 1: Restart Docker with pgvector

```bash
cd "D:\llm memory"

# Stop old container
docker-compose down -v

# Start with pgvector support
docker-compose up -d

# Verify it's running
docker logs llm_memory_postgres | grep "vector"
# Should see: "CREATE EXTENSION IF NOT EXISTS vector"
```

### Step 2: Install Dependencies

```bash
cd long-term-memory

# Install all packages
pip install -r requirements.txt
```

**First time?** This will download:
- `sentence-transformers` model (~400MB)
- May take 2-5 minutes depending on internet speed

### Step 3: Run!

```bash
python main.py
```

## What You'll See

```
📦 Loading embedding model: all-MiniLM-L6-v2...
✅ Embedding model loaded! Dimension: 384

============================================================
🧠 LLM with Long-term Memory (LTM)
============================================================
👤 User ID: user_1
🆔 Session ID: abc12345
============================================================

Commands:
  'quit' - Exit
  'memories' - View all stored memories
  'clear' - Clear all your data (STM + LTM)
  'stats' - View memory statistics
============================================================

You: 
```

## Example Conversation

### First Interaction

```
You: Hi, my name is Alex and I love building AI applications with Python

============================================================
💬 User: Hi, my name is Alex and I love building AI applications with Python
============================================================

🔍 Searching long-term memories...
   No relevant memories found

📝 Loading recent conversation (last 10 messages)...
   ✅ Loaded 1 messages from STM

🔧 Assembling context window...
   Context: 2 messages, ~145 tokens
   Breakdown: 1 system, 1 user, 0 assistant

🤖 Generating response...

🧠 Extracting memories...
   ✅ Memory created: [personal_info] User's name is Alex. Enjoys building AI applications using Python.
   Importance: 8/10
   💾 New memory stored in LTM

============================================================

🤖 Assistant: Hello Alex! It's wonderful to meet you! Building AI applications with Python...
```

### Later Interaction (Memory Retrieval)

```
You: What programming language do I prefer?

============================================================
💬 User: What programming language do I prefer?
============================================================

🔍 Searching long-term memories...
   ✅ Found 1 relevant memories:
   1. [personal_info] User's name is Alex. Enjoys building AI applications using Python.
      Relevance: 0.89 (similarity: 0.91, importance: 8/10)

📝 Loading recent conversation (last 10 messages)...
   ✅ Loaded 3 messages from STM

🔧 Assembling context window...
   Context: 4 messages, ~312 tokens
   Breakdown: 2 system, 2 user, 1 assistant

🤖 Generating response...

============================================================

🤖 Assistant: Based on our previous conversation, you prefer Python! You mentioned that you love building AI applications with it.
```

## View Stored Memories

```
You: memories

============================================================
💾 Stored Memories (1 total)
============================================================

1. [personal_info] Importance: 8/10
   Content: User's name is Alex. Enjoys building AI applications using Python.
   Created: 2025-01-21 14:30
   Accessed: 1 times (last: 2025-01-21 14:32)

============================================================
```

## How Semantic Search Works

**Example: Finding memories by meaning, not exact words**

```
Stored Memory:
"User enjoys building AI applications using Python"

Queries that will retrieve this memory:
✅ "What programming language do I like?" (similarity: 0.89)
✅ "What am I working on?" (similarity: 0.82)
✅ "Tell me about my coding preferences" (similarity: 0.91)
❌ "What's the weather?" (similarity: 0.12) - Too different
```

**Why it works:**
- Both "building AI applications" and "working on" have similar meanings
- "Python" and "programming language" are semantically related
- Embeddings capture these relationships!

## Understanding the Output

### Relevance Score Breakdown:

```
Relevance: 0.89 (similarity: 0.91, importance: 8/10)
           ↑                ↑                ↑
     Final score      Cosine similarity   User-set importance

Formula:
relevance = (0.91 × 0.7) + (0.8 × 0.3) = 0.637 + 0.24 = 0.877 ≈ 0.89
                ↑            ↑
          Similarity     Importance
          (70% weight)   (30% weight)
```

### Emphasis Levels in Context:

When building context for LLM, memories are emphasized based on relevance:

```
🔴 IMPORTANT [personal_info]: ...     (relevance ≥ 0.85)
🟡 Note [preference]: ...              (relevance ≥ 0.70)
⚪ [fact]: ...                          (relevance < 0.70)
```

## Testing Memory Extraction

Try these examples to see memory extraction in action:

### Personal Info
```
You: My name is Sarah and I'm 25 years old
Expected: Extracts "User's name is Sarah, age 25" (importance: 8-9)
```

### Preferences
```
You: I prefer dark mode interfaces and hate clutter
Expected: Extracts "User prefers dark mode, dislikes clutter" (importance: 6-7)
```

### Goals
```
You: I want to learn machine learning this year
Expected: Extracts "User goal: learn machine learning this year" (importance: 7-8)
```

### NOT Extracted (Too Generic)
```
You: What's the weather today?
Expected: No extraction (generic question, no personal info)
```

## Configuration Tuning

Edit `config.py` to customize behavior:

### Retrieval Settings
```python
MIN_SIMILARITY = 0.7    # Lower = more memories retrieved (may be less relevant)
                        # Higher = fewer memories (only very relevant)

TOP_K_MEMORIES = 5      # Max memories to retrieve per query
                        # Higher = more context, more tokens
```

### Weighting
```python
SIMILARITY_WEIGHT = 0.7    # How much semantic similarity matters
IMPORTANCE_WEIGHT = 0.3    # How much importance score matters

# Example adjustments:
# For factual Q&A: SIMILARITY_WEIGHT = 0.9, IMPORTANCE_WEIGHT = 0.1
# For personal assistant: SIMILARITY_WEIGHT = 0.6, IMPORTANCE_WEIGHT = 0.4
```

### Memory Limits
```python
STM_LIMIT = 10             # Recent messages to keep
                           # Higher = more context, more tokens

EXTRACT_EVERY_N_EXCHANGES = 1   # Extract after every exchange
                                # Set to 3 for less frequent extraction
```

## Performance Tips

### Faster Startup
The first run is slow due to model download. Subsequent runs are fast!

```
First run:  ~30 seconds (downloads model)
Later runs: ~3 seconds (model cached)
```

### Token Usage
Average token usage per request:

```
System prompt:        ~50 tokens
LTM memories (5):     ~200 tokens (depends on content)
STM messages (10):    ~500 tokens (depends on conversation)
Total:                ~750 tokens per request
```

### Database Performance
With 1000+ memories, search remains fast (~50-100ms) due to pgvector indexing.

## Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### "pgvector extension not found"
```bash
# Restart with pgvector image
docker-compose down -v
docker-compose up -d

# Verify
docker exec -it llm_memory_postgres psql -U llm_user -d llm_memory_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Embedding model download stuck
```bash
# Check internet connection
# Model downloads to: ~/.cache/torch/sentence_transformers/
# Delete cache and retry if stuck:
rm -rf ~/.cache/torch/sentence_transformers/
```

### Memory extraction not working
Check extractor output:
```python
# In memory_extractor.py, add debug print:
print(f"DEBUG: LLM response: {response.content}")
```

## What's Next?

After testing LTM, try:

1. **Test with different memory types**
   - Personal info, preferences, goals, decisions, facts

2. **Experiment with settings**
   - Adjust similarity thresholds
   - Change weighting formulas

3. **Multi-session testing**
   - Exit and restart
   - Verify memories persist across sessions

4. **Multi-user testing**
   - Use different user IDs
   - Verify memory isolation

5. **View database directly**
   ```sql
   SELECT * FROM ltm_memories ORDER BY created_at DESC;
   ```

Happy testing! 🚀
