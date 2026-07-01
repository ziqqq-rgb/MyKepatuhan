import { apiFetch, API_URL, authHeaders } from "./client";

export interface IngestJob {
  job_id: string;
  filename: string;
  status: "queued" | "processing" | "done" | "failed";
  started_at: string;
  finished_at?: string;
  error?: string;
}

export interface IngestedDocument {
  doc_name: string;
  filename: string;
  ingested_at: string;
  hash: string;
}

export async function apiUploadDocument(file: File): Promise<IngestJob> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API_URL}/ingest`, {
    method: "POST",
    headers: authHeaders(),
    body: fd,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail ?? "Upload failed");
  }
  return res.json();
}

export async function apiGetJobStatus(jobId: string): Promise<IngestJob> {
  return apiFetch<IngestJob>(`/ingest/status/${jobId}`);
}

export async function apiGetDocuments(): Promise<IngestedDocument[]> {
  return apiFetch<IngestedDocument[]>("/ingest/documents");
}