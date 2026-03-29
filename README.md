# E-Commerce Customer Support AI Agent

An AI-powered customer support agent built with **FastAPI**, **AWS Bedrock (Claude 3 Sonnet)**, **Qdrant (Docker)**, and **SQLite** — featuring RAG-based FAQ answering, Order Tracking, and Support Ticket creation.

---

## 🧠 Architecture

```
User → FastAPI (/chat, /clear) → Agent (AWS Bedrock Claude 3 + Tool Router)
                                          ↓
              ┌───────────────────────────┼──────────────────────────┐
              │                           │                          │
        RAG Tool                    Order Tool                Ticket Tool
  (Qdrant Docker +               (SQLite orders.db)       (SQLite tickets.db)
   Titan Embeddings)
```

**Key Design**: The agent is built **manually** using `bind_tools()` — no prebuilt agents, no LangGraph, no AgentExecutor.

---

## 📁 Project Structure

```
e-commerce-ai-agent/
│
├── app.py                  # FastAPI entry point
├── config.py               # Env vars & constants
├── docker-compose.yml      # Qdrant Docker setup
├── requirements.txt
├── .env.example
│
├── agent/
│   ├── agent.py            # Manual LLM + tool-calling loop
│   └── tools.py            # search_faq, track_order, create_support_ticket
│
├── rag/
│   ├── embeddings.py       # Bedrock Titan Embeddings V2
│   ├── qdrant_db.py        # Qdrant client (Docker)
│   └── faq_data.py         # 20 FAQ knowledge base entries
│
├── db/
│   ├── database.py         # SQLite helpers (init, get_order, create_ticket)
│   ├── seed_data.py        # 10 sample orders for testing
│   ├── orders.db           # Auto-created on startup
│   └── tickets.db          # Auto-created on startup
│
├── memory/
│   └── session.py          # In-memory session store (thread-safe)
│
└── models/
    └── schema.py           # Pydantic request/response schemas
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.11+
- Docker Desktop (running)
- AWS account with Bedrock access

### 2. Enable AWS Bedrock Models
In your AWS Console → Bedrock → Model Access, enable:
- `Claude 3 Sonnet` (`anthropic.claude-3-sonnet-20240229-v1:0`)
- `Amazon Titan Embeddings V2` (`amazon.titan-embed-text-v2:0`)

### 3. Clone & Configure
```bash
git clone <repo-url>
cd e-commerce-ai-agent

cp .env.example .env
# Edit .env with your AWS credentials
```

### 4. Start Qdrant (Docker)
```bash
docker compose up -d
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Server
```bash
uvicorn app:app --reload
```

Server starts at `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

---

## 🔌 API Endpoints

### `POST /chat`
Send a message to the support agent.

```json
// Request
{
  "message": "What is your return policy?",
  "session_id": "user-abc-123"
}

// Response
{
  "response": "We offer a 7-day hassle-free return policy...",
  "session_id": "user-abc-123"
}
```

### `POST /clear`
Clear a session's conversation history.

```json
// Request
{ "session_id": "user-abc-123" }

// Response
{ "message": "Session cleared successfully.", "session_id": "user-abc-123" }
```

### `GET /health`
Check system health.

```json
{
  "status": "ok",
  "components": {
    "qdrant": "connected",
    "sqlite": "ok"
  }
}
```

---

## 🧪 Test Scenarios

```bash
# FAQ - Return Policy
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your return policy?", "session_id": "s1"}'

# FAQ - Shipping
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How long does delivery take?", "session_id": "s1"}'

# Order Tracking
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Track my order ORD001, my mobile is 9999999999", "session_id": "s2"}'

# Support Ticket (multi-turn)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My product arrived damaged", "session_id": "s3"}'

# Clear Session
curl -X POST http://localhost:8000/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "s1"}'

# Health Check
curl http://localhost:8000/health
```

### Sample Orders for Testing

| Order ID | Mobile     | Status     | Product              |
|----------|------------|------------|----------------------|
| ORD001   | 9999999999 | shipped    | Wireless Headphones  |
| ORD002   | 8888888888 | delivered  | Running Shoes        |
| ORD003   | 7777777777 | processing | Smart Watch          |
| ORD005   | 5555555555 | shipped    | Bluetooth Speaker    |
| ORD010   | 9876543210 | processing | Winter Jacket        |

---

## 🛠️ Tech Stack

| Component        | Technology                              |
|------------------|-----------------------------------------|
| API Framework    | FastAPI + Uvicorn                       |
| LLM              | AWS Bedrock — Claude 3 Sonnet           |
| Embeddings       | AWS Bedrock — Amazon Titan Embeddings V2|
| Vector DB        | Qdrant (Docker)                         |
| Relational DB    | SQLite (orders.db + tickets.db)         |
| Session Memory   | In-memory dict (thread-safe)            |
| Agent Pattern    | Manual tool-calling loop (bind_tools)   |

---

## 🔑 Environment Variables

| Variable               | Description                          | Default     |
|------------------------|--------------------------------------|-------------|
| `AWS_ACCESS_KEY_ID`    | AWS IAM access key                   | required    |
| `AWS_SECRET_ACCESS_KEY`| AWS IAM secret key                   | required    |
| `AWS_REGION`           | AWS region for Bedrock               | `us-east-1` |
| `QDRANT_HOST`          | Qdrant host                          | `localhost` |
| `QDRANT_PORT`          | Qdrant port                          | `6333`      |