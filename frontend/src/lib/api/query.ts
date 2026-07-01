import { apiFetch } from "./client";

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