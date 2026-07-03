import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { apiFetch, ApiError, getToken, setToken, clearToken } from "./client";

const originalFetch = global.fetch;
const mockFetchOnce = (response: Partial<Response>) => {
  global.fetch = vi.fn().mockResolvedValue(response as Response);
};

describe("token storage", () => {
  beforeEach(() => localStorage.clear());

  it("returns null when no token is stored", () => {
    expect(getToken()).toBeNull();
  });

  it("stores and clears a token", () => {
    setToken("abc123");
    expect(getToken()).toBe("abc123");
    clearToken();
    expect(getToken()).toBeNull();
  });
});

describe("apiFetch", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("returns parsed JSON on success", async () => {
    mockFetchOnce({ ok: true, status: 200, json: async () => ({ id: "1" }) });
    await expect(apiFetch<{ id: string }>("/conversations")).resolves.toEqual({ id: "1" });
  });

  it("attaches the auth token when present", async () => {
    setToken("my-token");
    mockFetchOnce({ ok: true, status: 200, json: async () => ({}) });
    await apiFetch("/conversations");
    const [, options] = (global.fetch as any).mock.calls[0];
    expect(options.headers.Authorization).toBe("Bearer my-token");
  });

  it("returns undefined for a 204 response", async () => {
    mockFetchOnce({ ok: true, status: 204, json: async () => { throw new Error("not called"); } });
    await expect(apiFetch("/conversations/1")).resolves.toBeUndefined();
  });

  it("throws ApiError with the server's message on failure", async () => {
    mockFetchOnce({ ok: false, status: 400, json: async () => ({ detail: "Bad input" }) });
    await expect(apiFetch("/conversations")).rejects.toMatchObject({ message: "Bad input", status: 400 });
  });

  it("throws a network ApiError (status 0) when fetch itself fails", async () => {
    global.fetch = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(apiFetch("/conversations")).rejects.toMatchObject({ status: 0 });
  });

  it("parses Retry-After on a 429 response", async () => {
    mockFetchOnce({
      ok: false,
      status: 429,
      headers: new Headers({ "Retry-After": "30" }),
      json: async () => ({ detail: "Slow down" }),
    });
        let err!: ApiError;
    try {
    await apiFetch("/conversations");
    } catch (e) {
    err = e as ApiError;
    }
    expect(err).toBeInstanceOf(ApiError);
    expect(err.retryAfterSeconds).toBe(30);
  });

  describe("on 401", () => {
    const originalLocation = window.location;

    beforeEach(() => {
      setToken("stale-token");
      Object.defineProperty(window, "location", {
        configurable: true,
        value: { ...originalLocation, href: "" },
      });
    });
    afterEach(() => {
      Object.defineProperty(window, "location", { configurable: true, value: originalLocation });
    });

    it("clears the token and redirects to /login", async () => {
      mockFetchOnce({ ok: false, status: 401, json: async () => ({}) });
      await expect(apiFetch("/conversations")).rejects.toMatchObject({ status: 401 });
      expect(getToken()).toBeNull();
      expect(window.location.href).toBe("/login");
    });
  });
});