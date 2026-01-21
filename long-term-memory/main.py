from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import uuid
import config
from database import DatabaseManager
from memory_manager import MemoryManager
from context_builder import ContextBuilder

# ======================
# State Definition
# ======================
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    session_id: str

# ======================
# Initialize Components
# ======================
db = DatabaseManager()
memory_manager = MemoryManager()
context_builder = ContextBuilder()

llm = ChatOpenAI(
    model=config.MODEL_NAME,
    openai_api_key=config.OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
)

# ======================
# Graph Nodes
# ======================

def chat_node(state: State):
    """
    Main chat node with full LTM pipeline:
    LTM → Search → STM → Context Window → LLM
    """
    user_id = state["user_id"]
    session_id = state["session_id"]
    messages = state["messages"]
    
    # Get current user message
    user_message = messages[-1]
    
    # Store in STM
    db.add_stm_message(user_id, session_id, "user", user_message.content)
    
    print(f"\n{'='*60}")
    print(f"💬 User: {user_message.content}")
    print(f"{'='*60}\n")
    
    # ==================
    # STEP 1: LTM - Search & Retrieve
    # ==================
    print("🔍 Searching long-term memories...")
    relevant_memories = memory_manager.retrieve_relevant_memories(
        user_id=user_id,
        query=user_message.content
    )
    
    if relevant_memories:
        print(f"   ✅ Found {len(relevant_memories)} relevant memories:")
        for i, mem in enumerate(relevant_memories, 1):
            print(f"   {i}. [{mem['memory_type']}] {mem['content'][:60]}...")
            print(f"      Relevance: {mem['relevance_score']:.2f} (similarity: {mem['similarity']:.2f}, importance: {mem['importance']}/10)")
    else:
        print("   No relevant memories found")
    
    # ==================
    # STEP 2: STM - Get Recent Messages
    # ==================
    print(f"\n📝 Loading recent conversation (last {config.STM_LIMIT} messages)...")
    stm_messages = db.get_stm_messages(session_id, limit=config.STM_LIMIT)
    print(f"   ✅ Loaded {len(stm_messages)} messages from STM")
    
    # ==================
    # STEP 3: Context Window Assembly
    # ==================
    print("\n🔧 Assembling context window...")
    context = context_builder.build_context(
        ltm_memories=relevant_memories,
        stm_messages=stm_messages
    )
    
    # Get context stats
    stats = context_builder.get_context_stats(context)
    print(f"   Context: {stats['total_messages']} messages, ~{stats['estimated_tokens']} tokens")
    print(f"   Breakdown: {stats['system_messages']} system, {stats['user_messages']} user, {stats['assistant_messages']} assistant")
    
    # ==================
    # STEP 4: LLM Response Generation
    # ==================
    print("\n🤖 Generating response...")
    response = llm.invoke(context)
    
    # Store assistant response in STM
    db.add_stm_message(user_id, session_id, "assistant", response.content)
    
    # ==================
    # STEP 5: Memory Extraction (Post-Response)
    # ==================
    memory_created = memory_manager.create_memory(
        user_id=user_id,
        session_id=session_id,
        user_message=user_message.content,
        assistant_response=response.content
    )
    
    if memory_created:
        print("   💾 New memory stored in LTM")
    
    print(f"\n{'='*60}\n")
    
    return {"messages": [response]}

# ======================
# Build Graph
# ======================
def create_graph():
    """Create the LangGraph workflow"""
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("chat", chat_node)
    
    # Add edges
    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)
    
    return workflow.compile()

# ======================
# Interactive Chat Interface
# ======================
def run_chat():
    """Run interactive chat with long-term memory"""
    graph = create_graph()
    
    # User identification (in real app, this would be from auth)
    user_id = input("Enter your user ID (or press Enter for 'user_1'): ").strip() or "user_1"
    session_id = str(uuid.uuid4())[:8]  # Short session ID
    
    print("\n" + "="*60)
    print("🧠 LLM with Long-term Memory (LTM)")
    print("="*60)
    print(f"👤 User ID: {user_id}")
    print(f"🆔 Session ID: {session_id}")
    print("="*60)
    print("\nCommands:")
    print("  'quit' - Exit")
    print("  'memories' - View all stored memories")
    print("  'clear' - Clear all your data (STM + LTM)")
    print("  'stats' - View memory statistics")
    print("="*60 + "\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower() == 'memories':
            show_memories(user_id)
            continue
        
        if user_input.lower() == 'clear':
            confirm = input("⚠️  Clear ALL data (STM + LTM)? (yes/no): ").strip().lower()
            if confirm == 'yes':
                memory_manager.clear_user_data(user_id)
                print("🗑️  All data cleared!\n")
            continue
        
        if user_input.lower() == 'stats':
            show_stats(user_id, session_id)
            continue
        
        # Invoke the graph
        result = graph.invoke({
            "messages": [HumanMessage(content=user_input)],
            "user_id": user_id,
            "session_id": session_id
        })
        
        # Print AI response
        ai_message = result["messages"][-1]
        print(f"\n🤖 Assistant: {ai_message.content}\n")

def show_memories(user_id: str):
    """Display all stored memories for a user"""
    memories = memory_manager.get_user_memories(user_id)
    
    if not memories:
        print("\n📭 No memories stored yet\n")
        return
    
    print(f"\n{'='*60}")
    print(f"💾 Stored Memories ({len(memories)} total)")
    print(f"{'='*60}")
    
    for i, mem in enumerate(memories, 1):
        print(f"\n{i}. [{mem.memory_type}] Importance: {mem.importance}/10")
        print(f"   Content: {mem.content}")
        print(f"   Created: {mem.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Accessed: {mem.access_count} times (last: {mem.last_accessed.strftime('%Y-%m-%d %H:%M')})")
    
    print(f"\n{'='*60}\n")

def show_stats(user_id: str, session_id: str):
    """Show memory statistics"""
    ltm_count = len(memory_manager.get_user_memories(user_id))
    stm_count = len(db.get_stm_messages(session_id))
    
    print(f"\n{'='*60}")
    print(f"📊 Memory Statistics")
    print(f"{'='*60}")
    print(f"Long-term Memories (LTM): {ltm_count}")
    print(f"Short-term Messages (STM): {stm_count}")
    print(f"STM Limit: {config.STM_LIMIT}")
    print(f"LTM Retrieval: Top {config.TOP_K_MEMORIES}, Min Similarity: {config.MIN_SIMILARITY}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_chat()
