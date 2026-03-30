# E-Commerce Customer Support AI Agent

An AI-powered customer support agent built with **FastAPI**, **AWS Bedrock (Claude 3 Sonnet)**, **Qdrant (Docker)**, and **SQLite** — featuring RAG-based FAQ answering, Order Tracking, and Support Ticket creation.

---

## 🧠 Architecture

```
User (Frontend) → FastAPI (/chat, /clear) → Agent (AWS Bedrock Claude 3 + Tool Router)
                                           ↓
              ┌───────────────────────────┼──────────────────────────┐
              │                           │                          │
        RAG Tool                    Order Tool                Ticket Tool
  (Qdrant Docker +               (SQLite orders.db)       (SQLite tickets.db)
   Titan Embeddings)
```

**Key Design**: The agent is built **manually** using `bind_tools()` — no prebuilt agents, no LangGraph, no AgentExecutor.

---

## ✨ New Features

- **Modern Web Interface**: A sleek, dark-themed frontend for real-time interaction.
- **Persistent AI Memory**: Handles multi-turn conversations seamlessly using session-based memory.
- **One-Click Deployment**: Pre-built Docker images available on Docker Hub for quick setup.
- **Integrated RAG**: Instant answers from an FAQ knowledge base powered by Bedrock Titan Embeddings.
- **Tool Automation**: Automatic routing for Order Tracking and Support Ticket creation.

---

## 📁 Project Structure

```
e-commerce-ai-agent/
│
├── app.py                  # FastAPI entry point & API Implementation
├── config.py               # Env vars & constants
├── docker-compose.yml      # Docker setup (Hub images)
├── requirements.txt
├── .env.example
│
├── agent/
│   ├── agent.py            # Manual LLM + tool-calling loop (Core Logic)
│   └── tools.py            # search_faq, track_order, create_support_ticket
│
├── frontend/
│   ├── index.html          # Modern Dark UI
│   └── Dockerfile          # Nginx static setup
│
├── rag/
│   ├── embeddings.py       # Bedrock Titan Embeddings V2 (Vector Setup)
│   ├── qdrant_db.py        # Qdrant client (Vector Setup)
│   └── faq_data.py         # 20 FAQ knowledge base entries
│
├── db/
│   ├── database.py         # SQLite schema & helpers
│   ├── seed_data.py        # 10 sample orders for testing
│   ├── orders.db           # Auto-created on startup (Relational DB)
│   └── tickets.db          # Auto-created on startup (Relational DB)
│
├── memory/
│   └── session.py          # In-memory session store (thread-safe)
│
└── models/
    └── schema.py           # Pydantic request/response schemas (API Implementation)
```

---

## 🗄️ Database Schemas

### 1. Relational Database (SQLite)
The system uses two SQLite databases:

**`orders` table (`orders.db`)**
| Column          | Type    | Description                |
|-----------------|---------|----------------------------|
| `order_id`      | TEXT    | Primary Key (e.g., ORD001) |
| `mobile`        | TEXT    | Customer mobile number     |
| `status`        | TEXT    | order status (processing, shipped, etc.) |
| `product`       | TEXT    | Product name               |
| `delivery_date` | TEXT    | Estimated delivery date    |

**`tickets` table (`tickets.db`)**
| Column       | Type    | Description                     |
|--------------|---------|---------------------------------|
| `ticket_id`  | TEXT    | Primary Key (e.g., TCKTC49B)    |
| `name`       | TEXT    | Customer name                   |
| `mobile`     | TEXT    | Customer mobile                 |
| `issue`      | TEXT    | Detailed issue description      |
| `order_id`   | TEXT    | Associated Order ID (optional)  |
| `created_at` | TEXT    | Timestamp                       |

### 2. Vector Database (Qdrant)
- **Collection Name**: `ecommerce_faq`
- **Vector Size**: `1024` (Titan Embeddings V2)
- **Payload**: `{ "question": "...", "answer": "..." }`


---

## 🚀 Getting Started

> [!IMPORTANT]
> Before running the application in any mode, ensure you have a `.env` file with **correct AWS credentials**. Copy `.env.example` to `.env` and fill in your keys.

### Option 1: One-Click Docker Deployment (Recommended)
This method uses pre-built images from Docker Hub. You only need Docker and Docker Compose installed.

1. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION
   ```
2. **Launch Services**:
   ```bash
   docker-compose up -d
   ```
3. **Access the App**:
   - **Frontend**: `http://localhost:5000`
   - **Backend API**: `http://localhost:8000`
   - **Interactive Docs**: `http://localhost:8000/docs`

---

### Option 2: Manual Setup (Local Development)

#### 1. Backend Setup
1. **Prerequisites**: Python 3.11+
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Start Qdrant (Vector DB)**:
   ```bash
   docker compose up -d qdrant
   ```
4. **Run FastAPI Server**:
   ```bash
   uvicorn app:app --reload
   ```

#### 2. Frontend Setup
1. **Prerequisites**: Any local web server (Python's `http.server` is easiest).
2. **Run Frontend**:
   ```bash
   cd frontend
   python -m http.server 5000
   ```
3. **Access**: Open `http://localhost:5000` in your browser.

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
| Frontend         | Modern HTML5/CSS3 + Vanilla JS (Dark UI)|
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