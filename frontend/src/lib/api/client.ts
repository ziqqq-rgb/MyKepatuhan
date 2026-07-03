/**
 * Low-level HTTP client: token storage + a network-safe fetch wrapper.
 * Resource-specific API calls (auth, query, ingest) live in their own
 * files and import from here.
 */
const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

/**
 * Thrown for every non-2xx response and for network failures.
 * `status` is 0 for network-level failures (server unreachable), so
 * callers can tell "server said no" apart from "couldn't even connect".
 */
export class ApiError extends Error {
  status: number;
  retryAfterSeconds?: number;

  constructor(message: string, status: number, retryAfterSeconds?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

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

/** fetch() that turns "server unreachable / DNS / offline" into an ApiError
 * instead of letting a raw TypeError escape to the caller. */
export async function rawFetch(url: string, options: RequestInit): Promise<Response> {
  try {
    return await fetch(url, options);
  } catch {
    throw new ApiError("Could not reach the server. Check your connection and try again.", 0);
  }
}

/** Reads a JSON error body and throws the matching ApiError. Shared by
 * apiFetch and the raw multipart/form-encoded calls in auth.ts/ingest.ts,
 * so every request in the app fails the same way. */
export async function throwApiError(res: Response): Promise<never> {
  if (res.status === 429) {
    const retryAfterSeconds = Number(res.headers.get("Retry-After")) || undefined;
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      body.detail ?? "You're sending requests too quickly. Please wait a moment.",
      429,
      retryAfterSeconds
    );
  }

  const body = await res.json().catch(() => ({ detail: res.statusText }));
  const message = typeof body.detail === "string" ? body.detail : `Request failed (${res.status})`;
  throw new ApiError(message, res.status);
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await rawFetch(`${API_URL}${path}`, {
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
    throw new ApiError("Session expired. Please log in again.", 401);
  }

  if (!res.ok) {
    await throwApiError(res);
  }

  // DELETE endpoints return 204 with an empty body — res.json() would throw on that.
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

export { API_URL, authHeaders };