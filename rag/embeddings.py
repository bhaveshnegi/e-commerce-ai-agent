"""
AWS Bedrock Titan Embeddings V2 wrapper.
Embeds text into 1024-dimensional vectors.
"""
import json
import boto3
import config


def _get_bedrock_client():
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=config.AWS_REGION,
    )


def embed_text(text: str) -> list[float]:
    """
    Embed a single text string using Amazon Titan Embeddings V2.
    Returns a list of 1024 floats.
    """
    client = _get_bedrock_client()
    body = json.dumps({
        "inputText": text,
        "dimensions": config.EMBED_DIMENSIONS,
        "normalize": True,
    })
    response = client.invoke_model(
        modelId=config.BEDROCK_EMBED_MODEL,
        contentType="application/json",
        accept="application/json",
        body=body,
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts. Returns list of embedding vectors."""
    return [embed_text(t) for t in texts]
