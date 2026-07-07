import { apiFetch, API_URL, authHeaders, rawFetch, throwApiError } from "./client";

export interface Citation {
  rank: number;
  authority: string;
  topic: string;
  document_type: string;
  document_title: string;
  score: number;
  excerpt: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  citations: Citation[];
  no_results: boolean;
}

export async function apiQuery(
  question: string,
  authority?: string,
  topic?: string,
  conversationId?: string
): Promise<QueryResponse> {
  return apiFetch<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({
      question,
      authority: authority || undefined,
      topic: topic || undefined,
      conversation_id: conversationId || undefined,
    }),
  });
}

/** One streamed answer chunk from POST /query/stream. */
export interface StreamTokenEvent {
  text: string;
}

/** A failure surfaced mid-stream, after the 200 status has already been sent. */
export interface StreamErrorEvent {
  detail: string;
}

/**
 * Opens an SSE stream for the same /query contract as apiQuery(), but the
 * caller reads incremental "token" events instead of waiting for the full
 * answer. Read the returned Response with readSseStream() from "./stream".
 */
export async function apiQueryStream(
  question: string,
  authority?: string,
  topic?: string,
  conversationId?: string
): Promise<Response> {
  const res = await rawFetch(`${API_URL}/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      question,
      authority: authority || undefined,
      topic: topic || undefined,
      conversation_id: conversationId || undefined,
    }),
  });
  if (!res.ok) await throwApiError(res);
  return res;
}