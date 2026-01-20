from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import config
from database import DatabaseManager

# ======================
# State
# ======================
class State(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str


db = DatabaseManager()

llm = ChatOpenAI(
    model=config.MODEL_NAME,
    openai_api_key=config.OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
)

# ======================
# Summary Prompt
# ======================
SUMMARY_PROMPT = """
You are maintaining long-term memory for a conversation.

Rules:
- Summarize ONLY the given messages
- Keep factual details, goals, names
- Remove greetings and filler
- Do NOT invent information

Existing summary:
{existing_summary}

New messages:
{new_messages}

Updated summary:
"""

def generate_summary(existing_summary, text):
    prompt = SUMMARY_PROMPT.format(
        existing_summary=existing_summary or "None",
        new_messages=text
    )
    return llm.invoke([HumanMessage(content=prompt)]).content


# ======================
# Chat Node
# ======================
def chat_node(state: State):
    session_id = state["session_id"]
    user_msg = state["messages"][-1]

    # Store user message
    db.add_message(session_id, "user", user_msg.content)

    # Fetch all raw messages
    all_messages = db.get_messages(session_id)

    # 🔁 Summary logic (NO trimming)
    if len(all_messages) > config.STM_LIMIT:
        to_summarize = all_messages[:config.SUMMARY_CHUNK]

        text = "\n".join(
            f"{m.role}: {m.content}" for m in to_summarize
        )

        existing_summary = db.get_summary(session_id)
        new_summary = generate_summary(existing_summary, text)
        db.upsert_summary(session_id, new_summary)

        # Delete summarized messages
        db.delete_messages([m.id for m in to_summarize])

        print("🧠 Summary chunk created")

    # Fetch remaining STM
    stm_messages = db.get_messages(session_id)

    chat_history = []
    for m in stm_messages:
        if m.role == "user":
            chat_history.append(HumanMessage(content=m.content))
        else:
            chat_history.append(AIMessage(content=m.content))

    full_prompt = [
        SystemMessage(content="You are a helpful AI assistant.")
    ]

    summary = db.get_summary(session_id)
    if summary:
        full_prompt.append(
            SystemMessage(content=f"Conversation summary:\n{summary}")
        )

    full_prompt.extend(chat_history)

    response = llm.invoke(full_prompt)

    db.add_message(session_id, "assistant", response.content)

    return {"messages": [response]}


# ======================
# Graph
# ======================
def create_graph():
    g = StateGraph(State)
    g.add_node("chat", chat_node)
    g.add_edge(START, "chat")
    g.add_edge("chat", END)
    return g.compile()


def run_chat():
    graph = create_graph()
    session_id = "summary-only-session"

    print("🤖 Summary-based Memory Bot")
    print("Session:", session_id)

    while True:
        user_input = input("You: ").strip()
        if user_input == "quit":
            break

        result = graph.invoke({
            "messages": [HumanMessage(content=user_input)],
            "session_id": session_id
        })

        print("\nAssistant:", result["messages"][-1].content, "\n")


if __name__ == "__main__":
    run_chat()
