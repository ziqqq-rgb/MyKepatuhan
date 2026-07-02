import { apiFetch } from "./client";

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export async function apiCreateConversation(title = "New conversation"): Promise<Conversation> {
  return apiFetch<Conversation>("/conversations", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function apiListConversations(): Promise<Conversation[]> {
  return apiFetch<Conversation[]>("/conversations");
}

export async function apiGetConversationMessages(conversationId: string): Promise<ConversationMessage[]> {
  return apiFetch<ConversationMessage[]>(`/conversations/${conversationId}/messages`);
}

export async function apiDeleteConversation(conversationId: string): Promise<void> {
  await apiFetch<void>(`/conversations/${conversationId}`, { method: "DELETE" });
}