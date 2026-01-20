# LLM Memory Practice - Short-term Memory

This project implements three different short-term memory strategies for LLMs using LangGraph and PostgreSQL.

## Project Structure

```
llm memory/
├── docker-compose.yml          # PostgreSQL setup
├── .env                        # Environment variables (API keys, DB config)
├── .gitignore
└── short-term-memory/
    ├── trimming/               # Strategy 1: Message Trimming
    │   ├── main.py
    │   ├── config.py
    │   ├── database.py
    │   └── requirements.txt
    ├── summary/                # Strategy 2: Conversation Summary
    │   └── (to be implemented)
    └── user-progress/          # Strategy 3: User Progress Tracking
        └── (to be implemented)
```

## Setup Instructions

### 1. Configure Environment Variables

Edit the `.env` file and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 2. Start PostgreSQL with Docker

```bash
# Navigate to project folder
cd "D:\llm memory"

# Start PostgreSQL container
docker-compose up -d

# Check if container is running
docker ps
```

### 3. Install Python Dependencies

For the trimming strategy:

```bash
cd "short-term-memory\trimming"

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Run the Trimming Strategy

```bash
python main.py
```

## Strategy 1: Trimming

**How it works:**
- Keeps only the last N messages (default: 10)
- Automatically deletes older messages from PostgreSQL
- Simple sliding window approach

**Commands:**
- Type your message to chat
- `stats` - View current message count
- `clear` - Clear chat history
- `quit` - Exit

**Key Features:**
- Messages stored in PostgreSQL (`messages_trimming` table)
- Automatic trimming after each user message
- Session-based conversation tracking

## Stopping PostgreSQL

```bash
# Stop the container
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Next Steps

After testing the trimming strategy, we'll implement:
1. **Summary Strategy** - Periodically summarize old conversations
2. **User Progress Tracking** - Track user state and metadata

## Troubleshooting

**PostgreSQL connection error:**
- Make sure Docker is running
- Check if container is up: `docker ps`
- Verify port 5432 is not in use

**OpenRouter API error:**
- Verify your API key in `.env`
- Check if you have credits in OpenRouter

**Import errors:**
- Make sure you've installed all requirements
- Activate virtual environment if using one
