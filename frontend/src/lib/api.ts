const API_URL =
  (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

// ─────────────────────────────────────────
// TOKEN HELPERS
// ─────────────────────────────────────────
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("mk_token");
}

export function setToken(token: string): void {
  localStorage.setItem("mk_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("mk_token");
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers as Record<string, string> ?? {}),
    },
  });

  if (res.status === 401) {
    clearToken();
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `Request failed (${res.status})`);
  }

  return res.json();
}

// ─────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  is_admin: boolean;
}

export async function apiRegister(email: string, password: string): Promise<UserProfile> {
  return apiFetch<UserProfile>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function apiLogin(email: string, password: string): Promise<AuthResponse> {
  // FastAPI OAuth2 expects form-encoded body
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(err.detail ?? "Login failed");
  }
  return res.json();
}

export async function apiGetMe(): Promise<UserProfile> {
  return apiFetch<UserProfile>("/auth/me");
}

export async function apiOAuthLogin(email: string, token: string) {
  const res = await fetch(`${API_URL}/auth/oauth-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, token }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "OAuth Sync failed" }));
    throw new Error(err.detail ?? "OAuth Sync failed");
  }
  return res.json();
}

// ─────────────────────────────────────────
// QUERY
// ─────────────────────────────────────────
export interface Citation {
  rank: number;
  authority: string;
  topic: string;
  document_type: string;
  score: number;
  excerpt: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  citations: Citation[];
}

export async function apiQuery(
  question: string,
  authority?: string,
  topic?: string
): Promise<QueryResponse> {
  return apiFetch<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({
      question,
      authority: authority || undefined,
      topic: topic || undefined,
    }),
  });
}

// ─────────────────────────────────────────
// INGEST (admin only)
// ─────────────────────────────────────────
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
