"""
Builds the Citation list from a LlamaIndex query response's source nodes.
"""
from pydantic import BaseModel

EXCERPT_MAX_CHARS = 300


class Citation(BaseModel):
    rank: int
    authority: str
    topic: str
    document_type: str
    document_title: str
    score: float
    excerpt: str


def _truncate(text: str, max_chars: int = EXCERPT_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def build_citations(source_nodes: list) -> list[Citation]:
    """Converts LlamaIndex source nodes (ranked, post-rerank) into Citation objects."""
    return [
        Citation(
            rank=i + 1,
            authority=node.node.metadata.get("authority", "Unknown"),
            topic=node.node.metadata.get("topic", "Unknown"),
            document_type=node.node.metadata.get("document_type", "Unknown"),
            document_title=node.node.metadata.get("source_document", "Unknown source"),
            score=round(node.score or 0.0, 4),
            excerpt=_truncate(node.node.text),
        )
        for i, node in enumerate(source_nodes)
    ]