"""
Qdrant vector DB client.
Connects to Qdrant running in Docker on localhost:6333.
"""
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import config
from rag import embeddings

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        new_client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
        _client = new_client
    
    if _client is None:
        raise RuntimeError("Qdrant client could not be initialized.")
    return _client


def init_collection() -> None:
    """
    Create the FAQ collection if it doesn't already exist.
    Uses cosine similarity with 1024-dimensional Titan vectors.
    """
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if config.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=config.EMBED_DIMENSIONS,
                distance=Distance.COSINE,
            ),
        )
        print(f"[Qdrant] Created collection '{config.QDRANT_COLLECTION}'")
    else:
        print(f"[Qdrant] Collection '{config.QDRANT_COLLECTION}' already exists")


def upsert_faq(docs: list[str]) -> None:
    """
    Embed and upsert FAQ documents into Qdrant.
    Skips seeding if the collection already has documents.
    """
    client = get_client()
    count = client.count(collection_name=config.QDRANT_COLLECTION).count
    if count > 0:
        print(f"[Qdrant] FAQ already seeded ({count} docs). Skipping.")
        return

    print(f"[Qdrant] Seeding {len(docs)} FAQ documents...")
    vectors = embeddings.embed_batch(docs)
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={"text": doc},
        )
        for doc, vec in zip(docs, vectors)
    ]
    client.upsert(collection_name=config.QDRANT_COLLECTION, points=points)
    print(f"[Qdrant] Seeding complete.")


def search_faq(query: str, top_k: int = 3) -> list[str]:
    """
    Embed the query and return the top-k most relevant FAQ chunks.
    """
    client = get_client()
    query_vector = embeddings.embed_text(query)
    
    # query_points is the modern API in qdrant-client 1.17+
    results = client.query_points(
        collection_name=config.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return [hit.payload["text"] for hit in results.points]
