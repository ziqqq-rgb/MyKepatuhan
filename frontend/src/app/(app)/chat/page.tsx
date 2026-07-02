"use client";

import { useEffect, useRef, useState } from "react";
import { Menu, ShieldCheck } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { TypingDots } from "@/components/TypingDots";
import { useLanguage } from "@/lib/i18n";
import { apiQuery, apiGetConversationMessages } from "@/lib/api";
import { useConversations } from "@/lib/hooks/useConversations";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatInput } from "@/components/chat/ChatInput";
import { UserBubble } from "@/components/chat/UserBubble";
import { AssistantBubble } from "@/components/chat/AssistantBubble";
import type { Message, UserMessage } from "@/components/chat/constants";

export default function ChatPage() {
  const { tr } = useLanguage();
  const user = useUser();
  const {
    conversations,
    activeId,
    loading: conversationsLoading,
    select,
    startNew,
    createAndSelect,
    remove,
    refresh,
  } = useConversations();

  const [messages, setMessages] = useState<Message[]>([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [input, setInput] = useState("");
  const [authority, setAuthority] = useState("All");
  const [topic, setTopic] = useState("All");
  const [sending, setSending] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);


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

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  function buildNoResultsMessage(): string {
    const parts: string[] = [];
    if (authority !== "All") parts.push(`${tr("filter_authority")}: ${authority}`);
    if (topic !== "All") parts.push(`${tr("filter_topic")}: ${topic}`);
    const filtersStr = parts.length > 0 ? parts.join(` ${tr("chat_no_results_join")} `) : "";
    return tr("chat_no_results").replace("{filters}", filtersStr);
  }

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || sending) return;

    const isFirstMessageInConversation = messages.length === 0;

    const userMsg: UserMessage = { role: "user", content: trimmed, id: crypto.randomUUID() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
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

      const answer = res.no_results ? buildNoResultsMessage() : res.answer;

      setMessages((m) => [
        ...m,
        { role: "assistant", content: answer, citations: res.citations, id: crypto.randomUUID() },
      ]);

      // Backend sets the conversation's title from the first question —
      // refresh the sidebar so "New conversation" doesn't linger there.
      if (isFirstMessageInConversation) refresh();
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: tr("chat_error"), id: crypto.randomUUID() }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <Navbar variant="app" userEmail={user?.primaryEmail ?? undefined} />

      <div className="flex min-h-0 flex-1 overflow-hidden">
        <ChatSidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          conversations={conversations}
          activeId={activeId}
          loading={conversationsLoading}
          onSelect={(id) => {
            select(id);
            setSidebarOpen(false);
          }}
          onNewChat={() => {
            startNew();
            setSidebarOpen(false);
          }}
          onDelete={remove}
        />

        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-background/60 backdrop-blur-sm md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <main className="relative flex min-w-0 flex-1 flex-col">
          <div className="flex items-center border-b border-border bg-card/60 px-3 py-2 backdrop-blur-md md:hidden">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>

          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 h-64 opacity-40"
            style={{ background: "var(--gradient-hero)" }}
          />

          <div ref={scrollRef} className="relative flex-1 overflow-y-auto">
            {messagesLoading ? (
              <div className="flex h-full items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
              </div>
            ) : messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center px-4 py-12 text-center">
                <h2 className="mt-5 text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
                  {tr("chat_empty_title")}
                </h2>
                <div className="mt-8 grid w-full max-w-2xl gap-2.5 sm:grid-cols-3">
                  {(["chat_sugg_1", "chat_sugg_2", "chat_sugg_3"] as const).map((k) => (
                    <button
                      key={k}
                      onClick={() => send(tr(k))}
                      className="rounded-xl border border-border bg-card p-3.5 text-left text-sm text-foreground transition-all hover:border-primary/30 hover:bg-secondary hover:-translate-y-0.5"
                      style={{ boxShadow: "var(--shadow-sm)" }}
                    >
                      {tr(k)}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-6">
                {messages.map((m) =>
                  m.role === "user" ? <UserBubble key={m.id} message={m} /> : <AssistantBubble key={m.id} message={m} />
                )}
                {sending && (
                  <div className="flex items-start gap-2.5">
                    <div className="rounded-2xl rounded-tl-md border border-border bg-card px-4 py-3">
                      <TypingDots />
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <ChatInput
            input={input}
            onInputChange={setInput}
            onSend={() => send(input)}
            authority={authority}
            onAuthorityChange={setAuthority}
            topic={topic}
            onTopicChange={setTopic}
            loading={sending}
          />
        </main>
      </div>
    </div>
  );
}