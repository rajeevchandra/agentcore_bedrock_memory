from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider
import os, sys, boto3

REGION = "us-east-1"
ACTOR_ID = os.environ.get("ACTOR_ID", "raj")

# Do NOT default to any model here
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID")  # may be None or empty
PROFILE_ARN = os.environ.get("BEDROCK_INFERENCE_PROFILE_ARN")
SESSION_ID = "session-1"

# Ensure we're using the correct file
print(f"[module] __file__ = {__file__}")

# Memory ID
try:
    with open(".agentcore/memory_id.txt") as f:
        MEMORY_ID = f.read().strip()
except FileNotFoundError:
    print("ERROR: .agentcore/memory_id.txt not found. Run memory_setup.py first.", file=sys.stderr)
    sys.exit(1)

# Clients
memory_client = MemoryClient(region_name=REGION)
memory_provider = AgentCoreMemoryToolProvider(
    memory_id=MEMORY_ID,
    actor_id=ACTOR_ID,
    session_id=SESSION_ID,
    namespace=f"/users/{ACTOR_ID}",
    region=REGION,
)
brt = boto3.client("bedrock-runtime", region_name=REGION)

app = BedrockAgentCoreApp()

from botocore.exceptions import ParamValidationError

def call_llm(prompt: str) -> str:
    params = {"messages": [{"role": "user", "content": [{"text": prompt}]}]}
    # If a profile is set, ALWAYS use it and never fall back to modelId
    if PROFILE_ARN and PROFILE_ARN.strip():
        try:
            resp = brt.converse(inferenceProfileArn=PROFILE_ARN, **params)
            return resp["output"]["message"]["content"][0]["text"]
        except ParamValidationError as e:
            raise RuntimeError(
                f"Your boto3/botocore may be too old for inference profiles. "
                f"Upgrade with: pip install --upgrade boto3 botocore awscli\n{e}"
            )
    # Otherwise we need a modelId that supports on-demand
    if not MODEL_ID or not MODEL_ID.strip():
        raise RuntimeError(
            "No inference profile set and BEDROCK_MODEL_ID is empty. "
            "Either set BEDROCK_INFERENCE_PROFILE_ARN to use a profile, "
            "or set BEDROCK_MODEL_ID to an on-demand model (e.g. anthropic.claude-3-haiku-20240307-v1:0)."
        )
    resp = brt.converse(modelId=MODEL_ID.strip(), **params)
    return resp["output"]["message"]["content"][0]["text"]



@app.entrypoint
def invoke(payload: dict):
    user_prompt = payload.get("prompt", "Where should I eat?")

    # Read long-term prefs
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

    # Log short-term events
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
    print(f"[startup] REGION={REGION}")
    print(f"[startup] PROFILE_ARN={PROFILE_ARN or '(none)'}")
    print(f"[startup] MODEL_ID={MODEL_ID or '(none)'}")
    app.run()  # http://localhost:8080/invocations
