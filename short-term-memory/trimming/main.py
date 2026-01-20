from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import config
from database import DatabaseManager
import uuid

# Define the state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str

# Initialize database
db = DatabaseManager()

# Initialize LLM with OpenRouter
llm = ChatOpenAI(
    model=config.MODEL_NAME,
    openai_api_key=config.OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
)

def chat_node(state: State):
    """Main chat node that processes messages with trimming"""
    session_id = state["session_id"]
    messages = state["messages"]
    
    # Get the last user message
    last_message = messages[-1]
    
    # Store user message in database
    db.add_message(session_id, "user", last_message.content)
    
    # Trim old messages (keep only MAX_MESSAGES)
    deleted_count = db.trim_messages(session_id, config.MAX_MESSAGES)
    if deleted_count > 0:
        print(f"🗑️  Trimmed {deleted_count} old messages")
    
    # Get recent messages from database
    recent_messages = db.get_messages(session_id, limit=config.MAX_MESSAGES)
    
    # Convert database messages to LangChain format
    chat_history = []
    for msg in recent_messages:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))
    
    # Add system message
    system_msg = SystemMessage(content="You are a helpful AI assistant. Keep your responses concise and friendly.")
    full_messages = [system_msg] + chat_history
    
    # Get AI response
    response = llm.invoke(full_messages)
    
    # Store AI response in database
    db.add_message(session_id, "assistant", response.content)
    
    # Update state with AI response
    return {"messages": [response]}

# Build the graph
def create_graph():
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("chat", chat_node)
    
    # Add edges
    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)
    
    return workflow.compile()

def run_chat():
    """Run interactive chat with trimming memory"""
    graph = create_graph()
    session_id = str(uuid.uuid4())
    
    print("=" * 60)
    print("🤖 LLM Short-term Memory - TRIMMING Strategy")
    print(f"📝 Max messages kept: {config.MAX_MESSAGES}")
    print(f"🆔 Session ID: {session_id}")
    print("=" * 60)
    print("Type 'quit' to exit, 'clear' to clear history, 'stats' for statistics\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower() == 'clear':
            db.clear_session(session_id)
            print("🗑️  Chat history cleared!\n")
            continue
        
        if user_input.lower() == 'stats':
            messages = db.get_messages(session_id)
            print(f"\n📊 Statistics:")
            print(f"   Total messages in DB: {len(messages)}")
            print(f"   Max allowed: {config.MAX_MESSAGES}")
            print()
            continue
        
        if not user_input:
            continue
        
        # Invoke the graph
        result = graph.invoke({
            "messages": [HumanMessage(content=user_input)],
            "session_id": session_id
        })
        
        # Print AI response
        ai_message = result["messages"][-1]
        print(f"\nAssistant: {ai_message.content}\n")

if __name__ == "__main__":
    run_chat()
