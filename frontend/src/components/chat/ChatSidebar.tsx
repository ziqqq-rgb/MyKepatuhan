"use client";

import { Plus, X } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

// Placeholder history until real conversation persistence lands (see project notes).
const PLACEHOLDER_CONVERSATIONS = [
  "SSM registration steps",
  "Restaurant licensing in KL",
  "SST threshold 2025",
];

type ChatSidebarProps = {
  open: boolean;
  onClose: () => void;
  onNewChat: () => void;
};

export function ChatSidebar({ open, onClose, onNewChat }: ChatSidebarProps) {
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
        <button
          onClick={onClose}
          className="rounded p-1 text-muted-foreground hover:bg-secondary md:hidden"
        >
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
        {PLACEHOLDER_CONVERSATIONS.map((c) => (
          <button
            key={c}
            className="block w-full truncate rounded-md px-2 py-2 text-left text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          >
            {c}
          </button>
        ))}
      </div>
    </aside>
  );
}