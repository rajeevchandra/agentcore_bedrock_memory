from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider
import os, sys, boto3

REGION = "us-east-1"
ACTOR_ID = os.environ.get("ACTOR_ID", "raj")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-7-sonnet-20250219-v1:0")
PROFILE_ARN = os.environ.get("BEDROCK_INFERENCE_PROFILE_ARN")
SESSION_ID = "session-2"  # new session to prove recall

try:
    with open(".agentcore/memory_id.txt") as f:
        MEMORY_ID = f.read().strip()
except FileNotFoundError:
    print("ERROR: .agentcore/memory_id.txt not found. Run memory_setup.py first.", file=sys.stderr)
    sys.exit(1)

memory_provider = AgentCoreMemoryToolProvider(
    memory_id=MEMORY_ID,
    actor_id=ACTOR_ID,
    session_id=SESSION_ID,
    namespace=f"/users/{ACTOR_ID}",
    region=REGION,
)
memory_client = MemoryClient(region_name=REGION)
brt = boto3.client("bedrock-runtime", region_name=REGION)

app = BedrockAgentCoreApp()

def call_llm(prompt: str) -> str:
    params = {"messages": [{"role": "user", "content": [{"text": prompt}]}]}
    if PROFILE_ARN:
        resp = brt.converse(inferenceProfileArn=PROFILE_ARN, **params)
    else:
        resp = brt.converse(modelId=MODEL_ID, **params)
    return resp["output"]["message"]["content"][0]["text"]


@app.entrypoint
def invoke(payload: dict):
    user_prompt = payload.get("prompt", "Where should I eat (new session)?")

   
    
    mems = memory_client.retrieve_memories(
        memory_id=MEMORY_ID,
        namespace=f"/users/{ACTOR_ID}",
        query="Summarize the user's dining preferences.",
    )
    summary = (mems[0].get("text") if (mems and isinstance(mems[0], dict)) else str(mems[0])) if mems else "No saved preferences yet."

    prompt = (
        "You are Food Buddy. Use the user's persistent preferences when suggesting places.\n\n"
        f"Known preferences: {summary}\n\n"
        f"User asks: {user_prompt}\n\n"
        "Reply in 2-4 sentences."
    )

    answer = call_llm(prompt)

    try:
        memory_client.create_event(
            memory_id=MEMORY_ID,
            actor_id=ACTOR_ID,
            session_id=SESSION_ID,
            messages=[(user_prompt, "USER"), (answer, "ASSISTANT")],
        )
    except Exception as e:
        print(f"[warn] create_event failed: {e}", file=sys.stderr)

    return {"result": answer}

if __name__ == "__main__":
    print(f"[startup] Using model: {MODEL_ID} in {REGION}")
    app.run(port=8081)  # http://localhost:8081/invocations
