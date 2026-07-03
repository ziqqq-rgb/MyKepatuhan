"use client";

import { useEffect, useRef, useState } from "react";
import { Menu } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { TypingDots } from "@/components/TypingDots";
import { useLanguage } from "@/lib/i18n";
import { useRoleGate } from "@/lib/hooks/useRoleGate";
import { useConversations } from "@/lib/hooks/useConversations";
import { useChatMessages } from "@/lib/hooks/useChatMessages";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatInput } from "@/components/chat/ChatInput";
import { UserBubble } from "@/components/chat/UserBubble";
import { AssistantBubble } from "@/components/chat/AssistantBubble";

export default function ChatPage() {
  const { tr } = useLanguage();
  const user = useUser();
  const ready = useRoleGate("user", "/admin");

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

  const [input, setInput] = useState("");
  const [authority, setAuthority] = useState("All");
  const [topic, setTopic] = useState("All");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { messages, messagesLoading, sending, send } = useChatMessages({
    activeId,
    select,
    createAndSelect,
    onFirstMessageSent: refresh,
    authority,
    topic,
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  function handleSend() {
    send(input);
    setInput("");
  }

  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
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
            onSend={handleSend}
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