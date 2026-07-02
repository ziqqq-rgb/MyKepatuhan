"use client";

import { Plus, X, Trash2 } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import type { Conversation } from "@/lib/api";

type ChatSidebarProps = {
  open: boolean;
  onClose: () => void;
  conversations: Conversation[];
  activeId: string | null;
  loading: boolean;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onDelete: (id: string) => void;
};

export function ChatSidebar({
  open,
  onClose,
  conversations,
  activeId,
  loading,
  onSelect,
  onNewChat,
  onDelete,
}: ChatSidebarProps) {
  const { tr } = useLanguage();

  return (
    <aside
      className={`${
        open ? "fixed inset-y-0 left-0 z-50 flex shadow-xl" : "hidden"
      } w-60 shrink-0 flex-col border-r border-border bg-card md:relative md:flex`}
    >
      <div className="flex items-center justify-between border-b border-border p-3">
        <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {tr("chat_convos")}
        </span>
        <button onClick={onClose} className="rounded p-1 text-muted-foreground hover:bg-secondary md:hidden">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          style={{ background: "var(--gradient-primary)" }}
        >
          <Plus className="h-4 w-4" /> {tr("chat_new")}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-3 text-sm">
        {loading ? (
          <div className="flex justify-center py-6">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-primary" />
          </div>
        ) : conversations.length === 0 ? (
          <p className="px-2 py-4 text-center text-xs text-muted-foreground">{tr("chat_no_convos")}</p>
        ) : (
          conversations.map((c) => (
            <div
              key={c.id}
              className={`group flex items-center rounded-md transition-colors ${
                c.id === activeId ? "bg-secondary text-foreground" : "text-muted-foreground hover:bg-secondary/60"
              }`}
            >
              <button onClick={() => onSelect(c.id)} className="flex-1 truncate px-2 py-2 text-left" title={c.title}>
                {c.title}
              </button>
              <button
                onClick={() => onDelete(c.id)}
                className="mr-1 rounded p-1 opacity-0 hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100"
                aria-label="Delete conversation"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}