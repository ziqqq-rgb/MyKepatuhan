"use client";

import { useEffect, useRef, useState } from "react";
import { apiQuery, apiGetConversationMessages, ApiError } from "@/lib/api";
import { buildNoResultsMessage } from "@/lib/chat/noResultsMessage";
import { useLanguage } from "@/lib/i18n";
import type { Message, UserMessage } from "@/components/chat/constants";

type UseChatMessagesArgs = {
  activeId: string | null;
  select: (id: string | null) => void;
  createAndSelect: () => Promise<string>;
  onFirstMessageSent: () => void; // lets the sidebar refresh once the backend sets a real title
  authority: string;
  topic: string;
};

/**
 * Owns the message list for the active conversation: loads history when
 * the active conversation changes, and sends new questions. Conversation
 * *identity* stays in useConversations — this hook only owns its messages.
 */
export function useChatMessages({
  activeId,
  select,
  createAndSelect,
  onFirstMessageSent,
  authority,
  topic,
}: UseChatMessagesArgs) {
  const { tr } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const skipNextHistoryLoad = useRef(false);

  useEffect(() => {
    if (!activeId) {
      setMessages([]);
      return;
    }
    if (skipNextHistoryLoad.current) {
      skipNextHistoryLoad.current = false;
      return;
    }
    setMessagesLoading(true);
    apiGetConversationMessages(activeId)
      .then((history) => {
        setMessages(history.map((m) => ({ role: m.role, content: m.content, id: m.id }) as Message));
      })
      .catch(() => select(null)) // conversation no longer exists — fall back to a fresh chat
      .finally(() => setMessagesLoading(false));
  }, [activeId, select]);

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || sending) return;

    const isFirstMessageInConversation = messages.length === 0;
    const userMsg: UserMessage = { role: "user", content: trimmed, id: crypto.randomUUID() };
    setMessages((m) => [...m, userMsg]);
    setSending(true);

    try {
      let conversationId = activeId;
      if (!conversationId) {
        skipNextHistoryLoad.current = true;
        conversationId = await createAndSelect();
      }

      const res = await apiQuery(
        trimmed,
        authority === "All" ? undefined : authority,
        topic === "All" ? undefined : topic,
        conversationId
      );

      const answer = res.no_results ? buildNoResultsMessage(tr, authority, topic) : res.answer;
      setMessages((m) => [
        ...m,
        { role: "assistant", content: answer, citations: res.citations, id: crypto.randomUUID() },
      ]);

      if (isFirstMessageInConversation) onFirstMessageSent();
      } catch (err) {
        const content =
          err instanceof ApiError && err.status === 429
            ? tr("error_rate_limited")
            : err instanceof ApiError && err.status === 0
            ? tr("error_network")
            : tr("chat_error");
        setMessages((m) => [...m, { role: "assistant", content, id: crypto.randomUUID() }]);
      } finally {
        setSending(false);
      }
    }

  return { messages, messagesLoading, sending, send };
}