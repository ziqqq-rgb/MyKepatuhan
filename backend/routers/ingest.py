import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from database.models import User
from auth.utils import get_current_admin
from pipeline.ingestion.main import ingest_document
from pipeline.ingestion.checkpointing import load_hash_registry
from services import job_tracker

router = APIRouter(prefix="/ingest", tags=["Ingest (admin)"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class JobStatus(BaseModel):
    job_id: str
    filename: str
    status: str
    started_at: str
    finished_at: str | None = None
    error: str | None = None

class DocumentInfo(BaseModel):
    doc_name: str
    filename: str
    ingested_at: str
    hash: str

def run_ingestion(job_id: str, file_path: str, source_title: str) -> None:
    job_tracker.mark_processing(job_id)
    try:
        ingest_document(file_path, source_title=source_title)
        job_tracker.mark_done(job_id)
    except Exception as e:
        job_tracker.mark_failed(job_id, error=str(e))
    finally:
        if Path(file_path).exists():
            Path(file_path).unlink()

@router.post("", response_model=JobStatus)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    ):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    job_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{job_id}_{file.filename}"

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    job = job_tracker.create_job(job_id, file.filename)

    background_tasks.add_task(run_ingestion, job_id, str(save_path), file.filename)
    return job

@router.get("/status/{job_id}", response_model=JobStatus)
def get_job_status(
    job_id: str,
    admin: User = Depends(get_current_admin),
):
    """Check ingestion job status. Admin only."""
    job = job_tracker.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.get("/jobs", response_model=list[JobStatus])
def list_jobs(admin: User = Depends(get_current_admin)):
    """List all ingestion jobs this session. Admin only."""
    return job_tracker.list_jobs()


@router.get("/documents", response_model=list[DocumentInfo])
def list_documents(admin: User = Depends(get_current_admin)):
    """List all documents ingested into Pinecone. Admin only."""
    registry = load_hash_registry()
    return [
        DocumentInfo(
            doc_name=info["doc_name"],
            filename=info["file"],
            ingested_at=info["ingested_at"],
            hash=h[:12] + "...",
        )
        for h, info in registry.items()
    ]