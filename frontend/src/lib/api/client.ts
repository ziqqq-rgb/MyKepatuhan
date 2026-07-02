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

  // DELETE endpoints return 204 with an empty body — res.json() would throw on that.
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

export { API_URL, authHeaders };