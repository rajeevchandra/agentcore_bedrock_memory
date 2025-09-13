from bedrock_agentcore.memory import MemoryClient
import time, sys, os

REGION = "us-east-1"
ACTOR = os.environ.get("ACTOR_ID", "raj")
SESSION = os.environ.get("SESSION_ID", "lunch-chat-001")

try:
    with open(".agentcore/memory_id.txt") as f:
        MEMORY_ID = f.read().strip()
except FileNotFoundError:
    print("ERROR: .agentcore/memory_id.txt not found. Run memory_setup.py first.")
    sys.exit(1)

client = MemoryClient(region_name=REGION)

print("[1/2] Creating short-term events...")
client.create_event(
    memory_id=MEMORY_ID,
    actor_id=ACTOR,
    session_id=SESSION,
    messages=[
        ("I'm vegetarian and like quiet places.", "USER"),
        ("Noted. Any cuisine in mind?", "ASSISTANT"),
        ("Italian or Indian. Budget ~$30. I live in West Chester.", "USER"),
    ],
)
print("[OK] Events stored.")

print("[2/2] Waiting ~60s for long-term extraction...")
time.sleep(60)

print("[Query] Retrieving long-term preferences...")
mems = client.retrieve_memories(
    memory_id=MEMORY_ID,
    namespace=f"/users/{ACTOR}",
    query="Summarize the user's dining preferences",
)
print("Preferences:", mems)
