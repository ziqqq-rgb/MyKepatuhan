import type { Message } from "@/components/chat/constants";
import type { Citation } from "@/lib/api";

/** Appends a streamed text chunk to the assistant message with the given id. */
export function appendToMessage(messages: Message[], id: string, textChunk: string): Message[] {
  return messages.map((m) => (m.id === id && m.role === "assistant" ? { ...m, content: m.content + textChunk } : m));
}

/** Replaces an assistant message's content once streaming finishes or fails. */
export function finalizeMessage(messages: Message[], id: string, content: string, citations?: Citation[]): Message[] {
  return messages.map((m) => (m.id === id && m.role === "assistant" ? { ...m, content, citations } : m));
}