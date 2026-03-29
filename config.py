import os
from dotenv import load_dotenv

load_dotenv()

# ── AWS Bedrock ───────────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "ap-south-1")

# Bedrock model IDs
BEDROCK_LLM_MODEL   = "mistral.mistral-7b-instruct-v0:2"
BEDROCK_EMBED_MODEL = "amazon.titan-embed-text-v2:0"
EMBED_DIMENSIONS    = 1024  # Titan Embeddings V2 output size

# ── Qdrant ────────────────────────────────────────────────────────────────────
QDRANT_HOST       = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT       = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = "faq_knowledge_base"

# ── SQLite DB paths ───────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DB_DIR         = os.path.join(BASE_DIR, "db")
ORDERS_DB_PATH  = os.path.join(DB_DIR, "orders.db")
TICKETS_DB_PATH = os.path.join(DB_DIR, "tickets.db")
