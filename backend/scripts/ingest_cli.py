# scripts/ingest_cli.py
"""
Local ingestion entrypoint — run from VS Code / terminal, no server needed.

Usage:
    python -m scripts.ingest_cli ingest path/to/act_203_v1.pdf
    python -m scripts.ingest_cli batch path/to/folder/
    python -m scripts.ingest_cli delete-version act_203 1
"""
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("JOBLIB_MULTIPROCESSING", "0")

import argparse
import sys

from pipeline.ingestion.main import ingest_document, ingest_folder
from pipeline.ingestion.version_control import delete_document_version


def main() -> None:
    parser = argparse.ArgumentParser(description="MyKepatuhan ingestion CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a single PDF.")
    ingest_parser.add_argument("file_path")
    ingest_parser.add_argument("--title", default=None, help="Display title for citations.")

    batch_parser = subparsers.add_parser("batch", help="Ingest every PDF in a folder.")
    batch_parser.add_argument("folder_path")

    delete_parser = subparsers.add_parser("delete-version", help="Delete one version of a document from Pinecone.")
    delete_parser.add_argument("document_name")
    delete_parser.add_argument("version", type=int)

    args = parser.parse_args()

    try:
        if args.command == "ingest":
            ingest_document(args.file_path, source_title=args.title)
        elif args.command == "batch":
            ingest_folder(args.folder_path)
        elif args.command == "delete-version":
            delete_document_version(args.document_name, args.version)
    except Exception as e:
        print(f"❌ Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()