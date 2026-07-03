"""
Validates and safely persists uploaded PDF files.

Two checks happen before a file reaches the ingestion pipeline:
1. Magic-byte sniffing — a renamed .txt-to-.pdf won't pass this.
2. A streamed size cap — rejects an oversized upload mid-stream instead
   of buffering the whole thing into memory first.
"""
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from core import config

PDF_MAGIC_BYTES = b"%PDF-"
CHUNK_SIZE = 1024 * 1024  # read 1MB at a time


async def save_validated_pdf(file: UploadFile, destination: Path) -> None:
    """
    Streams `file` to `destination` in chunks, checking the PDF header
    up front and the size limit as it writes. On rejection, deletes any
    partial file so a failed upload leaves no debris on disk.
    """
    header = await file.read(len(PDF_MAGIC_BYTES))
    if not header.startswith(PDF_MAGIC_BYTES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid PDF.",
        )

    bytes_written = len(header)
    with open(destination, "wb") as out:
        out.write(header)
        while chunk := await file.read(CHUNK_SIZE):
            bytes_written += len(chunk)
            if bytes_written > config.MAX_UPLOAD_SIZE_BYTES:
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds the {config.MAX_UPLOAD_SIZE_MB}MB upload limit.",
                )
            out.write(chunk)