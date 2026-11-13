# agent.py - connects Gemini to the tools in agent_tools.py
import os
from google import genai
from google.genai import types
import agent_tools

# Client reads the key from the environment variable
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# The five tools Gemini is allowed to call
TOOLS = [
    agent_tools.get_segment_summary,
    agent_tools.lookup_client,
    agent_tools.compare_segments,
    agent_tools.top_clients,
    agent_tools.property_stats,
]

SYSTEM = (
    "You are a data analyst assistant for a real estate buyer segmentation project. "
    "Answer only from tool results and never invent numbers. "
    "If no tool can answer, say so."
)

def _new_chat():
    return client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM, tools=TOOLS),
    )

chat = _new_chat()

def reset_chat():
    global chat
    chat = _new_chat()
import time

def ask(question: str) -> str:
    # Retry a few times when Gemini is overloaded (503) or rate-limited (429)
    for attempt in range(4):
        try:
            return chat.send_message(question).text
        except Exception as e:
            busy = "503" in str(e)
            if busy and attempt < 3:
                time.sleep(2 ** attempt * 2)   # waits 2s, 4s, 8s
                continue
            raise

# Terminal test loop
if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        if q.lower() in ("exit", "quit"):
            break
        print(ask(q))