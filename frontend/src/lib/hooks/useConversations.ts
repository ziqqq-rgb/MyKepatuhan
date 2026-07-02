"use client";

import { useCallback, useEffect, useState } from "react";
import {
  apiListConversations,
  apiCreateConversation,
  apiDeleteConversation,
  type Conversation,
} from "@/lib/api";

const ACTIVE_ID_KEY = "mk_active_conversation_id";

/**
 * Owns the sidebar's conversation list and which one is active.
 * Persists the active id to localStorage so a page refresh restores the
 * same conversation instead of starting over. Message loading for the
 * active conversation is the chat page's job, not this hook's.
 */
export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setConversations(await apiListConversations());
    } catch {
      // A stale list on a transient network error beats wiping what's shown.
    }
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem(ACTIVE_ID_KEY);
    if (stored) setActiveId(stored);
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const select = useCallback((id: string | null) => {
    setActiveId(id);
    if (id) localStorage.setItem(ACTIVE_ID_KEY, id);
    else localStorage.removeItem(ACTIVE_ID_KEY);
  }, []);

  const startNew = useCallback(() => select(null), [select]);

  /** Creates a conversation on the backend and makes it active. Called lazily, on first send. */
  const createAndSelect = useCallback(async (): Promise<string> => {
    const conversation = await apiCreateConversation();
    setConversations((prev) => [conversation, ...prev]);
    select(conversation.id);
    return conversation.id;
  }, [select]);

  const remove = useCallback(
    async (id: string) => {
      await apiDeleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeId === id) select(null);
    },
    [activeId, select]
  );

  return { conversations, activeId, loading, select, startNew, createAndSelect, remove, refresh };
}