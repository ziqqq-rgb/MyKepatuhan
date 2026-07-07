"use client";

import { useEffect, useRef, useState } from "react";
import {
  apiQueryStream,
  apiGetConversationMessages,
  readSseStream,
  ApiError,
  type QueryResponse,
  type StreamTokenEvent,
  type StreamErrorEvent,
} from "@/lib/api";
import { buildNoResultsMessage } from "@/lib/chat/noResultsMessage";
import { appendToMessage, finalizeMessage } from "@/lib/chat/messageUpdates";
import { useLanguage } from "@/lib/i18n";
import type { Message, UserMessage } from "@/components/chat/constants";

type UseChatMessagesArgs = {
  activeId: string | null;
  select: (id: string | null) => void;
  createAndSelect: () => Promise<string>;
  onFirstMessageSent: () => void;
  authority: string;
  topic: string;
};

/**
 * Owns the message list for the active conversation: loads history when
 * the active conversation changes, and streams new answers token-by-token
 * from POST /query/stream.
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
      .catch(() => select(null))
      .finally(() => setMessagesLoading(false));
  }, [activeId, select]);

  /** Applies each SSE event from one /query/stream response to the given assistant message. */
  async function consumeStream(response: Response, assistantId: string, isFirstMessage: boolean) {
    for await (const { event, data } of readSseStream<StreamTokenEvent | QueryResponse | StreamErrorEvent>(response)) {
      if (event === "token") {
        setMessages((m) => appendToMessage(m, assistantId, (data as StreamTokenEvent).text));
      } else if (event === "done") {
        const result = data as QueryResponse;
        const text = result.no_results ? buildNoResultsMessage(tr, authority, topic) : result.answer;
        setMessages((m) => finalizeMessage(m, assistantId, text, result.citations));
        if (isFirstMessage) onFirstMessageSent();
      } else if (event === "error") {
        setMessages((m) => finalizeMessage(m, assistantId, tr("chat_error")));
      }
    }
  }

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || sending) return;

    const isFirstMessageInConversation = messages.length === 0;
    const userMsg: UserMessage = { role: "user", content: trimmed, id: crypto.randomUUID() };
    const assistantId = crypto.randomUUID();
    setMessages((m) => [...m, userMsg, { role: "assistant", content: "", id: assistantId }]);
    setSending(true);

    try {
      let conversationId = activeId;
      if (!conversationId) {
        skipNextHistoryLoad.current = true;
        conversationId = await createAndSelect();
      }

      const response = await apiQueryStream(
        trimmed,
        authority === "All" ? undefined : authority,
        topic === "All" ? undefined : topic,
        conversationId
      );
      await consumeStream(response, assistantId, isFirstMessageInConversation);
    } catch (err) {
      const content =
        err instanceof ApiError && err.status === 429
          ? tr("error_rate_limited")
          : err instanceof ApiError && err.status === 0
          ? tr("error_network")
          : tr("chat_error");
      setMessages((m) => finalizeMessage(m, assistantId, content));
    } finally {
      setSending(false);
    }
  }

  return { messages, messagesLoading, sending, send };
}