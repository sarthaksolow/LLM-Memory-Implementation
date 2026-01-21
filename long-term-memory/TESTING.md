# LTM Testing Scenarios

## Test Suite: Validate Your Implementation

### Scenario 1: Basic Memory Creation and Retrieval

**Objective:** Verify that personal information is extracted and retrieved correctly.

```
Test 1.1: Store Personal Info
─────────────────────────────
You: Hi! My name is Alex and I'm a software engineer from New York.

Expected Output:
✅ Memory created: [personal_info] User's name is Alex. Software engineer from New York.
   Importance: 8-9/10

Test 1.2: Retrieve Personal Info
─────────────────────────────────
(In same session or new session with same user_id)
You: What's my name?

Expected Output:
✅ Found 1 relevant memories
   [personal_info] User's name is Alex. Software engineer from New York.
   Relevance: ~0.85-0.95

🤖 Should mention: Your name is Alex
```

**Validation:**
- [ ] Memory was created
- [ ] Memory was retrieved when relevant
- [ ] Response used the retrieved memory

---

### Scenario 2: Preference Tracking

**Objective:** Test preference extraction and retrieval.

```
Test 2.1: Store Preferences
────────────────────────────
You: I prefer using Python for backend and React for frontend. I hate writing tests though.

Expected Output:
✅ Memory created: [preference] User prefers Python for backend, React for frontend. Dislikes writing tests.
   Importance: 7-8/10

Test 2.2: Retrieve Preferences
───────────────────────────────
You: What tech stack should I use for my new project?

Expected Output:
✅ Found 1 relevant memories
   Relevance: ~0.80-0.90

🤖 Should recommend: Python + React (based on preferences)
```

**Validation:**
- [ ] Preference extracted correctly
- [ ] Retrieved when discussing tech choices
- [ ] LLM incorporated preferences in recommendation

---

### Scenario 3: Goal Tracking

**Objective:** Verify goal extraction and progress tracking.

```
Test 3.1: Set Goal
──────────────────
You: This year, I want to learn Rust and build a CLI tool with it.

Expected Output:
✅ Memory created: [goal] User wants to learn Rust and build CLI tool this year.
   Importance: 8-9/10

Test 3.2: Check on Goal
───────────────────────
(Days later, same user)
You: What was my goal for this year again?

Expected Output:
✅ Found 1 relevant memories
   Relevance: ~0.90-0.95

🤖 Should mention: Learning Rust and building a CLI tool
```

**Validation:**
- [ ] Goal extracted with high importance
- [ ] Retrieved across sessions
- [ ] Persists in database

---

### Scenario 4: Semantic Search (Not Exact Match)

**Objective:** Test that semantic search works (not just keyword matching).

```
Test 4.1: Store Context
───────────────────────
You: I'm building a weather forecasting application using machine learning.

Expected Output:
✅ Memory created: [fact] User building weather forecasting app using ML.

Test 4.2: Semantic Query
────────────────────────
You: What am I working on with AI?

Expected Output:
✅ Found 1 relevant memories (despite "AI" vs "ML", "working on" vs "building")
   Similarity: ~0.75-0.85

🤖 Should answer: Weather forecasting application with machine learning
```

**Validation:**
- [ ] Retrieved despite different wording
- [ ] "AI" matched "machine learning" semantically
- [ ] "working on" matched "building" semantically

---

### Scenario 5: Multiple Related Memories

**Objective:** Test retrieval and ranking of multiple memories.

```
Test 5.1: Create Multiple Memories
───────────────────────────────────
You: My name is Sarah
✅ Memory: User's name is Sarah

You: I love Python programming
✅ Memory: User enjoys Python programming

You: I'm building a chatbot
✅ Memory: User building chatbot

You: I prefer functional programming style
✅ Memory: User prefers functional programming

Test 5.2: Query Multiple Memories
──────────────────────────────────
You: Tell me about my programming work

Expected Output:
✅ Found 3-4 relevant memories (top 5 limit)
   1. User building chatbot (relevance: ~0.90)
   2. User enjoys Python programming (relevance: ~0.85)
   3. User prefers functional programming (relevance: ~0.80)

🤖 Should synthesize: Mentions chatbot project, Python, functional style
```

**Validation:**
- [ ] Multiple relevant memories retrieved
- [ ] Sorted by relevance score
- [ ] Top 5 limit respected (config.TOP_K_MEMORIES)

---

### Scenario 6: Filtering Low Relevance

**Objective:** Test MIN_SIMILARITY threshold.

```
Test 6.1: Store Unrelated Memory
─────────────────────────────────
You: I have a dog named Max
✅ Memory: User has dog named Max

Test 6.2: Irrelevant Query
──────────────────────────
You: What programming languages do I know?

Expected Output:
❌ No relevant memories found (dog memory similarity < 0.7)

🤖 Should respond based only on STM, not mention dog
```

**Validation:**
- [ ] Low similarity memories filtered out
- [ ] MIN_SIMILARITY threshold (0.7) working
- [ ] Response doesn't hallucinate connections

---

### Scenario 7: Access Tracking

**Objective:** Verify access count and timestamps update.

```
Test 7.1: Create Memory
───────────────────────
You: I'm learning Spanish
✅ Memory created (access_count: 0)

Test 7.2: Use Memory Multiple Times
────────────────────────────────────
You: What languages am I learning?
✅ Retrieved (access_count: 1)

You: Help me practice the language I'm studying
✅ Retrieved (access_count: 2)

Test 7.3: Check Stats
─────────────────────
You: memories

Expected Output:
Content: User learning Spanish
Accessed: 2 times
```

**Validation:**
- [ ] access_count increments correctly
- [ ] last_accessed updates
- [ ] Stats displayed correctly

---

### Scenario 8: No Extraction for Generic Chat

**Objective:** Verify extractor doesn't create memories for small talk.

```
Test 8.1: Generic Messages
──────────────────────────
You: Hello!
❌ No memory created

You: How are you?
❌ No memory created

You: What's the weather today?
❌ No memory created

You: Thanks!
❌ No memory created
```

**Validation:**
- [ ] No memories created for greetings
- [ ] No memories for questions without personal info
- [ ] Extractor correctly identifies transient content

---

### Scenario 9: Decision Tracking

**Objective:** Test decision extraction.

```
Test 9.1: Make Decision
───────────────────────
You: I've decided to use PostgreSQL for my database instead of MongoDB.

Expected Output:
✅ Memory created: [decision] User chose PostgreSQL over MongoDB for database.
   Importance: 7-8/10

Test 9.2: Recall Decision
─────────────────────────
You: What database did I choose?

Expected Output:
✅ Found 1 relevant memories
🤖 Should answer: PostgreSQL
```

**Validation:**
- [ ] Decision extracted
- [ ] Retrieved when relevant
- [ ] Helps maintain consistency in recommendations

---

### Scenario 10: Cross-Session Persistence

**Objective:** Verify memories persist across sessions.

```
Test 10.1: Session 1
────────────────────
user_id: alex_123
You: My favorite color is blue
✅ Memory created
(Exit application)

Test 10.2: Session 2 (New Session, Same User)
──────────────────────────────────────────────
user_id: alex_123 (same user!)
You: What's my favorite color?

Expected Output:
✅ Found 1 relevant memories (from previous session!)
🤖 Should answer: Blue
```

**Validation:**
- [ ] Memory persists after restart
- [ ] Retrieved in new session
- [ ] user_id correctly isolates memories

---

### Scenario 11: Multi-User Isolation

**Objective:** Verify users don't see each other's memories.

```
Test 11.1: User 1
─────────────────
user_id: alice
You: My favorite language is Python
✅ Memory created for alice

Test 11.2: User 2 (Different User)
───────────────────────────────────
user_id: bob
You: What's my favorite language?

Expected Output:
❌ No relevant memories (alice's memories not retrieved)
🤖 Should say: I don't have that information
```

**Validation:**
- [ ] Memories isolated by user_id
- [ ] No cross-user data leakage
- [ ] Database queries filter by user_id

---

### Scenario 12: Context Window Assembly

**Objective:** Test proper context building with LTM + STM.

```
Test 12.1: Build Context
────────────────────────
Stored LTM: "User's name is Alex, enjoys Python"
Recent STM: Last 3 messages from current conversation

Expected Context Structure:
1. System: "You are a helpful AI assistant..."
2. System: "=== Relevant Information About User ===" (LTM)
3-5. Recent conversation messages (STM)
6. Current user query
```

**Validation:**
- [ ] Context includes system prompt
- [ ] LTM memories formatted with emphasis
- [ ] STM messages included chronologically
- [ ] Token count reasonable (~750 tokens)

---

## Performance Tests

### Test P1: Large Memory Count
```
Create 100+ memories
Query time should be < 200ms
Semantic search should still be fast (pgvector indexing)
```

### Test P2: Long Conversation
```
Send 50+ messages in one session
STM should trim to last 10
Memory extraction should still work
Response time should stay consistent
```

### Test P3: Embedding Speed
```
First query: ~2-3 seconds (model loaded)
Subsequent queries: < 1 second
Embedding generation should be fast
```

---

## Edge Cases

### Edge Case 1: Empty Query
```
You: (press Enter without text)
Expected: Should be skipped, no processing
```

### Edge Case 2: Very Long Message
```
You: (2000+ word message)
Expected: Should handle gracefully, may extract multiple memories
```

### Edge Case 3: Special Characters
```
You: I'm working on "Project X" with C++ & Rust!
Expected: Should extract correctly, handle special chars
```

---

## Debugging Commands

### View All Memories
```sql
SELECT id, user_id, memory_type, importance, content, access_count 
FROM ltm_memories 
ORDER BY created_at DESC;
```

### View STM
```sql
SELECT * FROM stm_messages 
WHERE session_id = 'your_session_id' 
ORDER BY timestamp;
```

### Check Similarity Manually
```python
from embeddings import embedding_manager

text1 = "I love Python programming"
text2 = "What programming language do I prefer?"

emb1 = embedding_manager.generate_embedding(text1)
emb2 = embedding_manager.generate_embedding(text2)

similarity = embedding_manager.compute_similarity(emb1, emb2)
print(f"Similarity: {similarity}")  # Should be ~0.75-0.85
```

---

## Success Criteria

Your LTM implementation is working correctly if:

✅ Memories are extracted only for important information  
✅ Semantic search finds relevant memories by meaning  
✅ Relevance scoring combines similarity + importance  
✅ Access tracking updates correctly  
✅ Memories persist across sessions  
✅ Users are isolated (no data leakage)  
✅ Context window assembly works properly  
✅ Performance is acceptable (< 3 seconds per query)  
✅ No extraction for generic chat  
✅ LLM responses use retrieved memories  

---

## Next Steps After Testing

1. **Tune Configuration**
   - Adjust MIN_SIMILARITY
   - Change relevance weights
   - Experiment with TOP_K_MEMORIES

2. **Add Features**
   - Memory consolidation (merge similar memories)
   - Memory decay (reduce importance over time)
   - Manual memory editing

3. **Optimize Performance**
   - Batch processing for multiple users
   - Caching for frequently accessed memories
   - Async processing

Happy Testing! 🧪🧠
