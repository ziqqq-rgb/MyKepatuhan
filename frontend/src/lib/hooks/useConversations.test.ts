import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { useConversations } from "./useConversations";
import * as api from "@/lib/api";

vi.mock("@/lib/api", () => ({
  apiListConversations: vi.fn(),
  apiCreateConversation: vi.fn(),
  apiDeleteConversation: vi.fn(),
}));

const mockConversations = [
  { id: "1", title: "Sdn Bhd registration", created_at: "2026-01-01" },
  { id: "2", title: "SST registration", created_at: "2026-01-02" },
];

describe("useConversations", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.mocked(api.apiListConversations).mockResolvedValue(mockConversations);
  });

  it("loads the conversation list on mount", async () => {
    const { result } = renderHook(() => useConversations());
    expect(result.current.loading).toBe(true);
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.conversations).toEqual(mockConversations);
  });

  it("restores the previously active id from localStorage", async () => {
    localStorage.setItem("mk_active_conversation_id", "2");
    const { result } = renderHook(() => useConversations());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.activeId).toBe("2");
  });

  it("creates a conversation and makes it active", async () => {
    const created = { id: "3", title: "New conversation", created_at: "2026-01-03" };
    vi.mocked(api.apiCreateConversation).mockResolvedValue(created);

    const { result } = renderHook(() => useConversations());
    await waitFor(() => expect(result.current.loading).toBe(false));

    let newId = "";
    await act(async () => {
      newId = await result.current.createAndSelect();
    });

    expect(newId).toBe("3");
    expect(result.current.activeId).toBe("3");
    expect(localStorage.getItem("mk_active_conversation_id")).toBe("3");
  });

  it("clears activeId when the active conversation is removed", async () => {
    vi.mocked(api.apiDeleteConversation).mockResolvedValue(undefined);
    localStorage.setItem("mk_active_conversation_id", "1");

    const { result } = renderHook(() => useConversations());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.remove("1");
    });

    expect(result.current.conversations.find((c) => c.id === "1")).toBeUndefined();
    expect(result.current.activeId).toBeNull();
  });
});