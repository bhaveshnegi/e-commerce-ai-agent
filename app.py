"""
FastAPI application — entry point.

Endpoints:
  POST /chat   — Send a message to the agent
  POST /clear  — Clear a session's chat history
  GET  /health — Health check (Qdrant + DB connectivity)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schema import ChatRequest, ChatResponse, ClearRequest, ClearResponse
from db import database
from db import seed_data
from rag import qdrant_db
from rag import faq_data
from memory import session
from agent.agent import agent


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("  E-Commerce AI Agent — Starting Up")
    print("=" * 50)

    # 1. Create SQLite tables
    database.init_db()

    # 2. Seed sample orders
    seed_data.seed_orders()

    # 3. Initialise Qdrant collection
    qdrant_db.init_collection()

    # 4. Seed FAQ documents into Qdrant
    qdrant_db.upsert_faq(faq_data.FAQ_DOCS)

    print("=" * 50)
    print("  Startup complete. Server is ready.")
    print("=" * 50)
    yield
    print("Server shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="E-Commerce Customer Support AI Agent",
    description=(
        "An AI-powered customer support agent with RAG (Qdrant), "
        "Order Tracking (SQLite), and Ticket Creation (SQLite), "
        "powered by AWS Bedrock Claude 3 Sonnet."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse, summary="Chat with the AI agent")
async def chat(request: ChatRequest):
    """
    Send a message to the e-commerce support agent.

    - **message**: The customer's message or question.
    - **session_id**: Unique identifier for this conversation (client-generated).
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id cannot be empty.")

    try:
        response_text = agent.run(
            session_id=request.session_id.strip(),
            user_message=request.message.strip(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    return ChatResponse(response=response_text, session_id=request.session_id)


@app.post("/clear", response_model=ClearResponse, summary="Clear a session's chat history")
async def clear(request: ClearRequest):
    """
    Clear the conversation history for a given session_id.
    Useful when the customer starts a new topic or conversation.
    """
    if not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id cannot be empty.")

    session.clear_session(request.session_id.strip())
    return ClearResponse(
        message="Session cleared successfully.",
        session_id=request.session_id,
    )


@app.get("/health", summary="Health check")
async def health():
    """Check the health of all system components."""
    status = {"status": "ok", "components": {}}

    # Check Qdrant
    try:
        client = qdrant_db.get_client()
        collections = client.get_collections()
        status["components"]["qdrant"] = "connected"
    except Exception as e:
        status["components"]["qdrant"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check SQLite DBs
    try:
        import sqlite3, config
        sqlite3.connect(config.ORDERS_DB_PATH).close()
        sqlite3.connect(config.TICKETS_DB_PATH).close()
        status["components"]["sqlite"] = "ok"
    except Exception as e:
        status["components"]["sqlite"] = f"error: {str(e)}"
        status["status"] = "degraded"

    return status
