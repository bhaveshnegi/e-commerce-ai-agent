"""
Hugging Face Sentence-Transformers Embeddings wrapper.
Uses local models for generating text vectors.
"""
from langchain_huggingface import HuggingFaceEmbeddings
import config

_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        print(f"[Embeddings] Loading HF model: {config.HF_EMBED_MODEL}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=config.HF_EMBED_MODEL,
            model_kwargs={'device': 'cpu'},  # Default to CPU for universal compatibility
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings


def embed_text(text: str) -> list[float]:
    """
    Embed a single text string using a Hugging Face model.
    """
    return get_embeddings().embed_query(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts. Returns a list of embedding vectors.
    """
    return get_embeddings().embed_documents(texts)
