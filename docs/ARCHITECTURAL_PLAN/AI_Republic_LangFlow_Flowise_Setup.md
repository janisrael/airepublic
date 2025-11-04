
# 🧠 AI Republic - LangFlow + Flowise Setup Guide

This guide explains how to set up the **Orchestrator (LangFlow)** and **Helpers (Flowise)** system for your AI Republic project — including port configuration, data flow, and Minion connections.

---

## ⚙️ 1️⃣ Install and Run LangFlow (Orchestrator)

**Install LangFlow:**
```bash
pip install langflow
```

**Run LangFlow:**
```bash
langflow run
```

Default UI: [http://localhost:7860](http://localhost:7860)

### 🧩 Create Orchestrator Flow
1. Add **Input Node (User Message)**
2. Connect to **LLM Node (Decision Model)**
3. Add **Conditional Router Node**
   - If query includes “SEO” → SEO Helper
   - If query includes “report” → Report Helper
   - Else → Knowledge Helper
4. Add **REST API Tool Nodes** to call Helper endpoints
   - Example: `POST http://localhost:6000/api/v1/predict`
5. End with **Output Node**

💾 Export to Python → `orchestrator_flow.py`

---

## ⚙️ 2️⃣ Setup Flowise (Helpers)

**Install Flowise:**
```bash
npx flowise start
```

Default UI: [http://localhost:3000](http://localhost:3000)

### Example Helpers:
| Helper | Port | Function |
|---------|------|-----------|
| SEO Helper | 6000 | WebSearch + LLM SEO optimization |
| Report Helper | 6001 | Data parser + PDF generator |
| Knowledge Helper | 6002 | RAG knowledge answering |

Run each instance:
```bash
PORT=6000 npx flowise start
PORT=6001 npx flowise start
PORT=6002 npx flowise start
```

Each flow will expose an endpoint like:
```
http://localhost:6000/api/v1/predict
```

---

## ⚙️ 3️⃣ Connect Orchestrator → Helpers

In LangFlow, edit REST nodes:

| Helper | Port | Endpoint |
|---------|------|-----------|
| SEO Helper | 6000 | `/api/v1/predict` |
| Report Helper | 6001 | `/api/v1/predict` |
| Knowledge Helper | 6002 | `/api/v1/predict` |

Now the Orchestrator can dynamically delegate tasks.

---

## ⚙️ 4️⃣ Setup Minion (Client Side)

Example Python WebSocket client:

```python
import websocket, json

ws = websocket.WebSocket()
ws.connect("ws://localhost:8000")

ws.send(json.dumps({"query": "Generate SEO report"}))
while True:
    print(ws.recv())
```

Browser version:
```js
const ws = new WebSocket("wss://ai-republic.com/orchestrator");
ws.onmessage = (event) => console.log(event.data);
```

✅ The Minion remains responsive, receiving async updates.

---

## ⚙️ 5️⃣ Optional: Nginx Reverse Proxy

```nginx
server {
    listen 80;

    location /orchestrator/ {
        proxy_pass http://localhost:8000/;
    }

    location /helpers/seo/ {
        proxy_pass http://localhost:6000/;
    }

    location /helpers/report/ {
        proxy_pass http://localhost:6001/;
    }

    location /helpers/knowledge/ {
        proxy_pass http://localhost:6002/;
    }
}
```

Now you can access:
```
http://ai-republic.com/orchestrator/
http://ai-republic.com/helpers/seo/
```

---

## ⚙️ 6️⃣ Docker Deployment

```bash
docker run -d -p 8000:7860 langflowai/langflow
docker run -d -p 6000:3000 flowiseai/flowise
docker run -d -p 6001:3000 flowiseai/flowise
docker run -d -p 6002:3000 flowiseai/flowise
```

---

## ✅ Final Architecture

```
User (Minion)
   ↓ WebSocket/API
Orchestrator (LangFlow - 8000)
   ↓ REST Calls
Helpers (Flowise)
   ├── SEO Helper - 6000
   ├── Report Helper - 6001
   └── Knowledge Helper - 6002
   ↓
Results stored → Cloud Storage / Nginx
```

---

## 🧩 Summary Port Map
| Component | Role | Port | Framework |
|------------|------|------|------------|
| Minion | Client | — | WebSocket |
| Orchestrator | Decision Flow | 8000 | LangFlow (LangGraph) |
| SEO Helper | Specialized Flow | 6000 | Flowise (LangChain) |
| Report Helper | Specialized Flow | 6001 | Flowise (LangChain) |
| Knowledge Helper | Specialized Flow | 6002 | Flowise (LangChain) |
