
# 🧠 AgentCore Memory Demo – Food Buddy  

This project demonstrates how to build **context-aware AI agents** with [Amazon Bedrock AgentCore (Preview)](https://aws.amazon.com/bedrock/) using **AgentCore Memory**.  

Most AI agents can handle a single interaction well, but they lose all context once the session ends. **True collaboration requires continuity** — that’s what AgentCore Memory enables.  

---

## 🔹 What is AgentCore Memory?  

AgentCore Memory is part of the Bedrock AgentCore runtime. It allows your agents to:  

### Short-Term Memory  
- Captures **raw events** (user + agent messages) within a session.  
- Maintains immediate context for ongoing conversations.  
- Example:  
  - You: “Suggest dinner places”  
  - You: “Make it vegetarian”  
  - The agent links both requests without needing repetition.  

### Long-Term Memory  
- Extracts **durable insights** like preferences, semantic facts, and summaries.  
- Stores them in a namespace tied to the user (e.g. `/users/{actorId}`).  
- Example:  
  - Last week you said you like vegetarian Italian food.  
  - This week you just ask: “Where should I eat tonight?”  
  - The agent recalls your stored preference and tailors the response.  

Together, these layers let agents feel less like stateless bots and more like **adaptive collaborators**.  

---

## ⚙️ Architecture Overview  

```text
User → AgentCore Runtime → Bedrock Model
     ↘ short-term events ↙
       AgentCore Memory
           ↓
    Long-term facts / summaries
```

- **Short-term events**: logged automatically during each session.  
- **Strategies**: run in the background to extract long-term insights.  
- **Long-term memory**: retrieved across sessions for personalization.  

---

## 🍝 The Food Buddy Demo  

This repo implements a simple “Food Buddy” agent that:  
- Saves **short-term events** while you interact.  
- Extracts preferences into **long-term memory**.  
- Uses those preferences in later sessions to personalize dinner suggestions.  

### Session 1  
```text
> Suggest dinner places
> Make it vegetarian
```
Agent links the two and gives vegetarian options.  

### Session 2 (next day)  
```text
> Where should I eat tonight?
```
Agent recalls you like vegetarian Italian, and suggests accordingly.  

---

## 🚀 Getting Started  

### Prerequisites  
- Python 3.10+  
- AWS CLI configured with access to Bedrock in your region  
- Model access: either **ON_DEMAND modelId** or an **Inference Profile ARN**  

### Setup  
```bash
git clone https://github.com/rajeevchandra/agentcore_bedrock_memory
cd agentcore_bedrock_memory

python -m venv venv
source venv/bin/activate   # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
```

### Configure Model Access  

**Option A: ON_DEMAND model**  
```bash
export BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
export BEDROCK_INFERENCE_PROFILE_ARN=
```

**Option B: Inference Profile**  
```bash
export BEDROCK_INFERENCE_PROFILE_ARN=arn:aws:bedrock:us-east-1:123456789:inference-profile/...
export BEDROCK_MODEL_ID=
```

### Run  

1. Create memory + seed sample preferences:  
```bash
python memory_setup.py
python seed_events.py
```

2. Start Food Buddy agent (session 1):  
```bash
python food_buddy.py
```

3. Call it:  
```bash
curl -X POST http://localhost:8080/invocations   -H "Content-Type: application/json"   -d '{"prompt":"Suggest dinner places"}'
```

4. Start a new session (session 2) and test long-term recall:  
```bash
python food_buddy_new_session.py
curl -X POST http://localhost:8081/invocations   -H "Content-Type: application/json"   -d '{"prompt":"Where should I eat tonight?"}'
```

---

<img width="1536" height="1024" alt="ChatGPT Image Sep 13, 2025, 03_33_46 PM" src="https://github.com/user-attachments/assets/0df73549-5bb6-46c8-a540-3d1f550cb1d8" />

```

---

## 🧰 Troubleshooting  

- **AccessDeniedException**: Ensure the model you’re using is *granted* in your account/region.  
- **Unknown parameter `inferenceProfileArn`**: Upgrade your SDK:  
  ```bash
  pip install --upgrade boto3 botocore
  ```  
- **No preferences returned**: Wait ~60s after running `seed_events.py` for extraction strategies to update long-term memory.  

---

## 📎 Resources  

- [Amazon Bedrock AgentCore Memory blog](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/)  
- [Bedrock documentation](https://docs.aws.amazon.com/bedrock/)  

---

👉 With memory, AI agents stop being reactive Q&A bots and start becoming **context-aware partners**.  
