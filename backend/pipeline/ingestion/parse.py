from pathlib import Path
from pipeline.ingestion.logger import log
from pipeline.ingestion.checkpointing import checkpoint_exists, load_checkpoint, save_checkpoint

def stage_parse(file_path: str) -> list:
    """Parse PDF using Docling and chunk into nodes."""
    doc_name = Path(file_path).stem

    if checkpoint_exists("nodes_raw", doc_name):
        log.info(f"[SKIP] Parsing already done for '{doc_name}'. Loading checkpoint.")
        return load_checkpoint("nodes_raw", doc_name)

    log.info(f"[START] Parsing '{file_path}'...")

    from docling.chunking import HybridChunker
    from llama_index.readers.docling import DoclingReader
    from llama_index.node_parser.docling import DoclingNodeParser
    from llama_index.embeddings.ollama import OllamaEmbedding
    from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
    from transformers import AutoTokenizer

    # FIX: use the embedding model's own tokenizer, not Qwen
    EMBED_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
    MAXTOKEN = 512

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_NAME),
        max_tokens=MAXTOKEN,
    )

    chunker = HybridChunker(tokenizer=tokenizer)

    reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)
    documents = reader.load_data(file_path=[file_path])

    node_parser = DoclingNodeParser(chunker=chunker)
    nodes = node_parser.get_nodes_from_documents(documents)

    log.info(f"[DONE] Parsed {len(nodes)} nodes from '{doc_name}'.")
    save_checkpoint("nodes_raw", doc_name, nodes)
    return nodes