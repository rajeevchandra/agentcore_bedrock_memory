# 🍝 Food Buddy – Amazon Bedrock AgentCore Memory Demo (us-east-1)

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
