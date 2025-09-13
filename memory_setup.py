# memory_setup.py (idempotent + valid name)
from bedrock_agentcore.memory import MemoryClient
from botocore.exceptions import ClientError
import os, time, random, string

REGION = "us-east-1"
client = MemoryClient(region_name=REGION)

os.makedirs(".agentcore", exist_ok=True)
MEMO_FILE = ".agentcore/memory_id.txt"

def rand_suffix(n=6):
    # letters+digits only to satisfy [a-zA-Z0-9_]
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

# 0) Reuse existing ID if present
if os.path.exists(MEMO_FILE):
    with open(MEMO_FILE) as f:
        memory_id = f.read().strip()
    print(f"[reuse] Using existing Memory ID from {MEMO_FILE}: {memory_id}")
else:
    base_name = "FoodBuddyMemory"
    name = base_name
    print("[1/3] Creating Memory...")
    try:
        memory = client.create_memory(
            name=name,
            description="Short-term + long-term dining preferences memory",
        )
        memory_id = memory.get("id") or memory.get("memoryId") or memory["id"]
        print(f"[OK] Memory ID: {memory_id}")
    except ClientError as e:
        msg = str(e)
        # If name exists, retry ONCE with a valid underscore suffix
        if "already exists" in msg:
            name = f"{base_name}_{rand_suffix()}"
            # Ensure <= 48 chars
            name = name[:48]
            print(f"[info] Name '{base_name}' exists. Retrying with '{name}'...")
            memory = client.create_memory(
                name=name,
                description="Short-term + long-term dining preferences memory",
            )
            memory_id = memory.get("id") or memory.get("memoryId") or memory["id"]
            print(f"[OK] Memory ID: {memory_id}")
        else:
            print("Failed to create memory:", e)
            raise

print("[2/3] Adding long-term strategy (User Preferences)...")
try:
    strategy = client.add_user_preference_strategy(
        memory_id=memory_id,
        name="UserPreferences",
        namespaces=["/users/{actorId}"],
    )
    print("[OK] Strategy added:", strategy.get("name", "UserPreferences"))
except ClientError as e:
    # If strategy already exists, continue
    if "already exists" in str(e) or "ValidationException" in str(e):
        print("[info] Strategy likely exists already; continuing.")
    else:
        print("Failed to add strategy:", e)
        raise

print("[3/3] Waiting ~60s for strategy to become ACTIVE...")
time.sleep(60)

with open(MEMO_FILE, "w") as f:
    f.write(memory_id)
print(f"[DONE] Memory ready. ID saved to {MEMO_FILE}")
