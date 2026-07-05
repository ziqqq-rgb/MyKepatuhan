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
    excerpt: str


def _truncate(text: str, max_chars: int = EXCERPT_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def build_citations(source_nodes: list) -> list[Citation]:
    """
    Converts reranked source nodes into citation cards for display.

    Nodes are already sorted best-first by the reranker. When several
    chunks come from the same document, only the highest-scored one is
    kept — otherwise the same document shows up as 2-3 near-identical
    cards in the sources panel. This only affects what's *displayed*;
    the LLM still sees every retrieved chunk during generation.
    """
    seen_documents: set[str] = set()
    citations: list[Citation] = []

    for node in source_nodes:
        title = node.node.metadata.get("source_document", "Unknown source")
        if title in seen_documents:
            continue
        seen_documents.add(title)

        citations.append(
            Citation(
                rank=len(citations) + 1,
                authority=node.node.metadata.get("authority", "Unknown"),
                topic=node.node.metadata.get("topic", "Unknown"),
                document_type=node.node.metadata.get("document_type", "Unknown"),
                document_title=title,
                score=round(node.score or 0.0, 4),
                excerpt=_truncate(node.node.text),
            )
        )

    return citations