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
    Handles recreation if there's a vector dimension mismatch.
    """
    client = get_client()
    try:
        # Check if collection exists and has the correct dimensions
        info = client.get_collection(config.QDRANT_COLLECTION)
        # Handle both single vector and named vectors config
        if hasattr(info.config.params.vectors, 'size'):
            existing_size = info.config.params.vectors.size
        else:
            # Fallback for complex configs if needed
            existing_size = None

        if existing_size and existing_size != config.EMBED_DIMENSIONS:
            print(f"[Qdrant] Dimension mismatch ({existing_size} -> {config.EMBED_DIMENSIONS}). Recreating '{config.QDRANT_COLLECTION}'...")
            client.delete_collection(config.QDRANT_COLLECTION)
            # Create fresh
            client.create_collection(
                collection_name=config.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=config.EMBED_DIMENSIONS,
                    distance=Distance.COSINE,
                ),
            )
        else:
            print(f"[Qdrant] Collection '{config.QDRANT_COLLECTION}' ready.")
    except Exception:
        # Collection doesn't exist, create it
        client.create_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=config.EMBED_DIMENSIONS,
                distance=Distance.COSINE,
            ),
        )
        print(f"[Qdrant] Created collection '{config.QDRANT_COLLECTION}' ({config.EMBED_DIMENSIONS} dims).")


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
