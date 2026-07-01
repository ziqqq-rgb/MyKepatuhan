import { apiFetch, API_URL } from "./client";

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
  // FastAPI's OAuth2PasswordRequestForm expects a form-encoded body, not JSON.
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

export async function apiOAuthLogin(email: string) {
  const res = await fetch(`${API_URL}/auth/oauth-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "OAuth Sync failed" }));
    const message = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
    throw new Error(message);
  }

  return res.json();
}