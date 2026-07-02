"use client";

import { useState } from "react";
import { Plus, X, Trash2, PanelLeftClose, PanelLeftOpen, MessageSquare } from "lucide-react";
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
  // Desktop-only rail collapse — separate from the mobile drawer's open/close.
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`${
        open ? "fixed inset-y-0 left-0 z-50 flex shadow-2xl" : "hidden"
      } ${collapsed ? "md:w-[72px]" : "md:w-64"} w-64 shrink-0 flex-col border-r border-border bg-card transition-[width] duration-200 ease-out md:relative md:flex`}
    >
      {/* Header */}
      <div className={`flex h-14 items-center border-b border-border ${collapsed ? "md:justify-center md:px-0" : "justify-between"} px-3`}>
        <span
          className={`text-[11px] font-semibold uppercase tracking-wider text-muted-foreground ${
            collapsed ? "md:hidden" : ""
          }`}
        >
          {tr("chat_convos")}
        </span>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="hidden rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground md:flex"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </button>
        <button onClick={onClose} className="rounded-lg p-1.5 text-muted-foreground hover:bg-secondary md:hidden">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* New chat */}
      <div className={`p-3 ${collapsed ? "md:px-2" : ""}`}>
        <button
          onClick={onNewChat}
          title={tr("chat_new")}
          className={`flex w-full items-center rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 active:scale-[0.98] ${
            collapsed ? "md:justify-center md:px-0 md:py-2.5" : "justify-center gap-2 px-3 py-2.5"
          }`}
          style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-elegant)" }}
        >
          <Plus className="h-4 w-4 shrink-0" />
          <span className={collapsed ? "md:hidden" : ""}>{tr("chat_new")}</span>
        </button>
      </div>

      {/* Conversation list */}
      <div className={`flex-1 overflow-y-auto overflow-x-hidden pb-3 text-sm ${collapsed ? "md:px-2" : "px-2"}`}>
        {loading ? (
          <div className="flex justify-center py-6">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-primary" />
          </div>
        ) : conversations.length === 0 ? (
          <p className={`px-2 py-4 text-center text-xs text-muted-foreground ${collapsed ? "md:hidden" : ""}`}>
            {tr("chat_no_convos")}
          </p>
        ) : (
          conversations.map((c) => (
            <div
              key={c.id}
              title={collapsed ? c.title : undefined}
              className={`group mb-0.5 flex items-center rounded-lg transition-colors ${
                c.id === activeId
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
              }`}
            >
              <button
                onClick={() => onSelect(c.id)}
                className={`flex flex-1 items-center gap-2.5 overflow-hidden text-left ${
                  collapsed ? "md:justify-center md:px-2.5 md:py-2.5" : "px-2.5 py-2.5"
                }`}
              >
                <MessageSquare className="h-3.5 w-3.5 shrink-0 opacity-70" />
                <span className={`truncate ${collapsed ? "md:hidden" : ""}`}>{c.title}</span>
              </button>
              <button
                onClick={() => onDelete(c.id)}
                className={`mr-1 shrink-0 rounded-md p-1.5 opacity-0 transition-opacity hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100 ${
                  collapsed ? "md:hidden" : ""
                }`}
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