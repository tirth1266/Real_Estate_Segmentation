# agent.py - connects Gemini to the tools in agent_tools.py
import os
import time
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
    "Call the fewest tools needed, usually one. For comparisons use compare_segments only. "
    "If no tool can answer, say so."
)


def _new_chat():
    return client.chats.create(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            tools=TOOLS,
            # keep thinking minimal so each model call is fast
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )


chat = _new_chat()


def reset_chat():
    global chat
    chat = _new_chat()


def ask(question: str) -> str:
    # Retry when Gemini is overloaded (503); print timings to the terminal
    for attempt in range(4):
        t = time.time()
        try:
            text = chat.send_message(question).text
            print(f"ask() ok in {time.time() - t:.1f}s (attempt {attempt + 1})")
            return text
        except Exception as e:
            print(f"attempt {attempt + 1} failed after {time.time() - t:.1f}s: {e}")
            if "503" in str(e) and attempt < 3:
                time.sleep(2 ** attempt * 2)   # waits 2s, 4s, 8s
                continue
            raise


# Terminal test loop (must stay at the very bottom of the file)
if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        if q.lower() in ("exit", "quit"):
            break
        print(ask(q))