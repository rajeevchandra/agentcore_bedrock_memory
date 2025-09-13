🧠 AgentCore Memory Demo – Food Buddy

This project demonstrates how to build context-aware AI agents with Amazon Bedrock AgentCore (Preview)
 using AgentCore Memory.

Most AI agents can handle a single interaction well, but they lose all context once the session ends. True collaboration requires continuity — that’s what AgentCore Memory enables.

🔹 What is AgentCore Memory?

AgentCore Memory is part of the Bedrock AgentCore runtime. It allows your agents to:

Short-Term Memory

Captures raw events (user + agent messages) within a session.

Maintains immediate context for ongoing conversations.

Example:

You: “Suggest dinner places”

You: “Make it vegetarian”

The agent links both requests without needing repetition.

Long-Term Memory

Extracts durable insights like preferences, semantic facts, and summaries.

Stores them in a namespace tied to the user (e.g. /users/{actorId}).

Example:

Last week you said you like vegetarian Italian food.

This week you just ask: “Where should I eat tonight?”

The agent recalls your stored preference and tailors the response.

Together, these layers let agents feel less like stateless bots and more like adaptive collaborators.

⚙️ Architecture Overview
User → AgentCore Runtime → Bedrock Model
     ↘ short-term events ↙
       AgentCore Memory
           ↓
    Long-term facts / summaries


Short-term events: logged automatically during each session.

Strategies: run in the background to extract long-term insights.

Long-term memory: retrieved across sessions for personalization.

🍝 The Food Buddy Demo

This repo implements a simple “Food Buddy” agent that:

Saves short-term events while you interact.

Extracts preferences into long-term memory.

Uses those preferences in later sessions to personalize dinner suggestions

<img width="1536" height="1024" alt="ChatGPT Image Sep 13, 2025, 03_33_46 PM" src="https://github.com/user-attachments/assets/09bc33b7-90db-4219-b722-a36f24ce9b72" />


This demo runs in **us-east-1** region by default.  
It shows how to build a context-aware agent using **Amazon Bedrock AgentCore Memory**.

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) Create memory (writes ID to .agentcore/memory_id.txt)
python memory_setup.py

# 2) Seed a few chat turns (extracts long-term prefs)
python seed_events.py

# 3) Run the agent locally
python food_buddy.py
curl -s -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d '{"prompt":"Suggest dinner places"}'
```

## Deploy to AWS AgentCore Runtime

```bash
# Linux/macOS
bash scripts/deploy_aws.sh
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/deploy_aws.ps1
```

## Cleanup

```bash
# Linux/macOS
bash scripts/destroy_aws.sh
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/destroy_aws.ps1
```
