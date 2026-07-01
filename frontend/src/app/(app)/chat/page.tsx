"use client";

import { useEffect, useRef, useState } from "react";
import { Menu, ShieldCheck } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { TypingDots } from "@/components/TypingDots";
import { useLanguage } from "@/lib/i18n";
import { apiQuery } from "@/lib/api";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatInput } from "@/components/chat/ChatInput";
import { UserBubble } from "@/components/chat/UserBubble";
import { AssistantBubble } from "@/components/chat/AssistantBubble";
import type { Message, UserMessage } from "@/components/chat/constants";

export default function ChatPage() {
  const { tr } = useLanguage();
  const user = useUser();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [authority, setAuthority] = useState("All");
  const [topic, setTopic] = useState("All");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the latest message.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  /** Builds the localized "no results under {filters}" message from active filters. */
  function buildNoResultsMessage(): string {
    const parts: string[] = [];
    if (authority !== "All") parts.push(`${tr("filter_authority")}: ${authority}`);
    if (topic !== "All") parts.push(`${tr("filter_topic")}: ${topic}`);
    const filtersStr = parts.length > 0 ? parts.join(` ${tr("chat_no_results_join")} `) : "";
    return tr("chat_no_results").replace("{filters}", filtersStr);
  }

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const userMsg: UserMessage = { role: "user", content: trimmed, id: crypto.randomUUID() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await apiQuery(
        trimmed,
        authority === "All" ? undefined : authority,
        topic === "All" ? undefined : topic
      );

      const answer = res.no_results ? buildNoResultsMessage() : res.answer;

      setMessages((m) => [
        ...m,
        { role: "assistant", content: answer, citations: res.citations, id: crypto.randomUUID() },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: tr("chat_error"), id: crypto.randomUUID() },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <Navbar variant="app" userEmail={user?.primaryEmail ?? undefined} />

      <div className="flex min-h-0 flex-1 overflow-hidden">
        <ChatSidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onNewChat={() => {
            setMessages([]);
            setSidebarOpen(false);
          }}
        />

        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <main className="flex min-w-0 flex-1 flex-col">
          <div className="flex items-center border-b border-border bg-card px-3 py-2 md:hidden">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded p-1.5 text-muted-foreground hover:bg-secondary"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center px-4 py-12 text-center">
                <div
                  className="flex h-16 w-16 items-center justify-center rounded-2xl border border-border text-white shadow-sm"
                  style={{ background: "var(--gradient-primary)" }}
                >
                  <ShieldCheck className="h-8 w-8" strokeWidth={2} />
                </div>
                <h2 className="mt-5 text-2xl font-semibold text-foreground sm:text-3xl">
                  {tr("chat_empty_title")}
                </h2>
                <div className="mt-8 grid w-full max-w-2xl gap-2.5 sm:grid-cols-3">
                  {(["chat_sugg_1", "chat_sugg_2", "chat_sugg_3"] as const).map((k) => (
                    <button
                      key={k}
                      onClick={() => send(tr(k))}
                      className="rounded-xl border border-border bg-card p-3.5 text-left text-sm text-foreground transition-all hover:border-primary/30 hover:bg-secondary hover:-translate-y-0.5"
                    >
                      {tr(k)}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mx-auto flex w-full max-w-3xl flex-col gap-5 px-4 py-6">
                {messages.map((m) =>
                  m.role === "user" ? (
                    <UserBubble key={m.id} message={m} />
                  ) : (
                    <AssistantBubble key={m.id} message={m} />
                  )
                )}
                {loading && (
                  <div className="flex justify-start">
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
            loading={loading}
          />
        </main>
      </div>
    </div>
  );
}