/**
 * Low-level HTTP client: token storage + a generic authenticated fetch
 * wrapper. Resource-specific API calls (auth, query, ingest) live in
 * their own files and import `apiFetch` from here.
 */
const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

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

/**
 * Generic authenticated JSON fetch. Adds the bearer token, redirects to
 * /login on 401, and throws with the server's error detail on failure.
 */
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
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

/** Exposed for resource files that need to build raw fetch calls (e.g. multipart uploads, form-encoded bodies). */
export { API_URL, authHeaders };