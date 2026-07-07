"use client";

import { useEffect, useRef, useState } from "react";
import { Menu } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { useRoleGate } from "@/lib/hooks/useRoleGate";
import { useConversations } from "@/lib/hooks/useConversations";
import { useChatMessages } from "@/lib/hooks/useChatMessages";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatEmptyState } from "@/components/chat/ChatEmptyState";
import { ChatMessageList } from "@/components/chat/ChatMessageList";

export default function ChatPage() {
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

  // Keep the transcript pinned to the newest message as it grows,
  // including token-by-token while an answer is streaming in.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  function handleSend() {
    send(input);
    setInput("");
  }

  function handleSelectConversation(id: string) {
    select(id);
    setSidebarOpen(false);
  }

  function handleNewChat() {
    startNew();
    setSidebarOpen(false);
  }

  if (!ready) return <FullScreenSpinner />;

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
          onSelect={handleSelectConversation}
          onNewChat={handleNewChat}
          onDelete={remove}
        />

        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-background/60 backdrop-blur-sm md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <main className="relative flex min-w-0 flex-1 flex-col">
          <MobileSidebarToggle onOpen={() => setSidebarOpen(true)} />

          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 h-64 opacity-40"
            style={{ background: "var(--gradient-hero)" }}
          />

          <div ref={scrollRef} className="relative flex-1 overflow-y-auto">
            {messagesLoading ? (
              <div className="flex h-full items-center justify-center">
                <Spinner />
              </div>
            ) : messages.length === 0 ? (
              <ChatEmptyState onSuggestionClick={send} />
            ) : (
              <ChatMessageList messages={messages} sending={sending} />
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

/** Spinning ring, unstyled by container — callers decide sizing/centering. */
function Spinner() {
  return <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />;
}

/** Full-viewport variant of Spinner, shown while the role gate resolves. */
function FullScreenSpinner() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <Spinner />
    </div>
  );
}

/** Hamburger button that opens the conversation sidebar; hidden on desktop where the sidebar is always visible. */
function MobileSidebarToggle({ onOpen }: { onOpen: () => void }) {
  return (
    <div className="flex items-center border-b border-border bg-card/60 px-3 py-2 backdrop-blur-md md:hidden">
      <button
        onClick={onOpen}
        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
      >
        <Menu className="h-5 w-5" />
      </button>
    </div>
  );
}