"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Menu, Plus, ShieldCheck, X } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { TypingDots } from "@/components/TypingDots";
import { useLanguage } from "@/lib/i18n";
import { apiQuery, type Citation } from "@/lib/api";

type UserMessage = { role: "user"; content: string; id: string };
type AssistantMessage = { role: "assistant"; content: string; citations?: Citation[]; id: string };
type Message = UserMessage | AssistantMessage;

type FilterOption = { value: string; label: string };

const AUTHORITIES: FilterOption[] = [
  { value: "All", label: "All" },
  { value: "SSM", label: "SSM" },
  { value: "KKM", label: "KKM" },
  { value: "DBKL", label: "DBKL" },
  { value: "MPKj", label: "MPKj" },
  { value: "LHDN", label: "LHDN" },
  { value: "MyIPO", label: "MyIPO" },
];

const TOPICS: FilterOption[] = [
  { value: "All", label: "All" },
  { value: "registration", label: "Registration" },
  { value: "tax", label: "Tax" },
  { value: "licensing", label: "Licensing" },
  { value: "zoning", label: "Zoning" },
  { value: "employment", label: "Employment" },
  { value: "compliance", label: "Compliance" },
];

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
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 140) + "px";
  }, [input]);

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

    let answer = res.answer;
    if (res.no_results) {
      const parts: string[] = [];
      if (authority !== "All") parts.push(`${tr("filter_authority")}: ${authority}`);
      if (topic !== "All") parts.push(`${tr("filter_topic")}: ${topic}`);
      const filtersStr = parts.length > 0 ? parts.join(` ${tr("chat_no_results_join")} `) : "";
      answer = tr("chat_no_results").replace("{filters}", filtersStr);
    }

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
        {/* ── Sidebar ── */}
        <aside
          className={`${
            sidebarOpen ? "fixed inset-y-0 left-0 z-50 flex shadow-xl" : "hidden"
          } w-60 shrink-0 flex-col border-r border-border bg-card md:relative md:flex`}
        >
          <div className="flex items-center justify-between border-b border-border p-3">
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              {tr("chat_convos")}
            </span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="rounded p-1 text-muted-foreground hover:bg-secondary md:hidden"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="p-3">
            <button
              onClick={() => { setMessages([]); setSidebarOpen(false); }}
              className="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
              style={{ background: "var(--gradient-primary)" }}
            >
              <Plus className="h-4 w-4" /> {tr("chat_new")}
            </button>
          </div>

          {/* Placeholder conversation history */}
          <div className="flex-1 overflow-y-auto px-2 pb-3 text-sm">
            {["SSM registration steps", "Restaurant licensing in KL", "SST threshold 2025"].map((c) => (
              <button
                key={c}
                className="block w-full truncate rounded-md px-2 py-2 text-left text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                {c}
              </button>
            ))}
          </div>
        </aside>

        {/* Sidebar backdrop on mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* ── Main ── */}
        <main className="flex min-w-0 flex-1 flex-col">
          {/* Mobile topbar */}
          <div className="flex items-center border-b border-border bg-card px-3 py-2 md:hidden">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded p-1.5 text-muted-foreground hover:bg-secondary"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto">
            {messages.length === 0 ? (
              /* Empty state */
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
                    <div key={m.id} className="flex justify-end">
                      <div
                        className="max-w-[80%] rounded-2xl rounded-tr-md px-4 py-2.5 text-sm text-white"
                        style={{ background: "var(--gradient-primary)" }}
                      >
                        {m.content}
                      </div>
                    </div>
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

          {/* ── Input area ── */}
          <div className="border-t border-border bg-card">
            <div className="mx-auto w-full max-w-3xl px-4 py-3">
              <div className="rounded-2xl border border-border bg-background p-2 transition-colors focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/10">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send(input);
                    }
                  }}
                  placeholder={tr("chat_placeholder")}
                  rows={1}
                  className="block max-h-[140px] w-full resize-none bg-transparent px-2 py-1.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
                />
                <div className="mt-1 flex items-center justify-between gap-2 px-1">
                  <div className="flex items-center gap-2">
                    <FilterSelect
                      label={tr("filter_authority")}
                      value={authority}
                      onChange={setAuthority}
                      options={AUTHORITIES}
                      allLabel={tr("filter_all")}
                    />
                    <FilterSelect
                      label={tr("filter_topic")}
                      value={topic}
                      onChange={setTopic}
                      options={TOPICS}
                      allLabel={tr("filter_all")}
                    />
                  </div>
                  <button
                    onClick={() => send(input)}
                    disabled={!input.trim() || loading}
                    className="flex h-8 w-8 items-center justify-center rounded-lg text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
                    style={{ background: "var(--gradient-primary)" }}
                  >
                    <ArrowUp className="h-4 w-4" strokeWidth={2.5} />
                  </button>
                </div>
              </div>
              <p className="mt-2 text-center text-xs text-muted-foreground">
                {tr("chat_disclaimer")}
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

// ── Sub-components ──

function FilterSelect({
  label, value, onChange, options, allLabel,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: FilterOption[];
  allLabel: string;
}) {
  return (
    <label className="flex items-center gap-1 rounded-md border border-border bg-card px-2 py-1 text-xs text-muted-foreground">
      <span className="hidden sm:inline">{label}:</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-transparent text-foreground focus:outline-none"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.value === "All" ? allLabel : o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function AssistantBubble({ message }: { message: AssistantMessage }) {
  const { tr } = useLanguage();
  const [open, setOpen] = useState(false);
  const count = message.citations?.length ?? 0;

  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] rounded-2xl rounded-tl-md border border-border bg-card px-4 py-3.5 text-sm text-foreground">
        <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
        {count > 0 && (
          <div className="mt-3 border-t border-border pt-3">
            <button
              onClick={() => setOpen((o) => !o)}
              className="text-xs font-medium text-primary hover:underline"
            >
              {open ? tr("chat_hide_sources") : tr("chat_show_sources")} ({count})
            </button>
            {open && (
              <div className="mt-3 space-y-2">
                {message.citations!.map((c, i) => (
                  <div key={i} className="rounded-xl bg-secondary p-3 text-xs">
                    <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                      <span className="font-semibold text-foreground">{c.document_title}</span>
                      <span className="ml-auto font-mono text-muted-foreground">{c.score.toFixed(2)}</span>
                    </div>
                    <div className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-muted-foreground">
                      <span>{c.authority}</span>
                      {c.topic && <span>· {c.topic}</span>}
                      {c.document_type && <span>· {c.document_type}</span>}
                    </div>
                    {c.excerpt && (
                      <p className="mt-2 font-mono text-[11px] leading-relaxed text-muted-foreground">
                        {c.excerpt}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
