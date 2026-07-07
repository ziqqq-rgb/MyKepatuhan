"use client";

import { useLanguage, type TranslationKey } from "@/lib/i18n";

const SUGGESTION_KEYS: TranslationKey[] = ["chat_sugg_1", "chat_sugg_2", "chat_sugg_3"];

type ChatEmptyStateProps = {
  onSuggestionClick: (question: string) => void;
};

/** Shown before the first message in a conversation: headline plus a few starter questions. */
export function ChatEmptyState({ onSuggestionClick }: ChatEmptyStateProps) {
  const { tr } = useLanguage();

  return (
    <div className="flex h-full flex-col items-center justify-center px-4 py-12 text-center">
      <h2 className="mt-5 text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
        {tr("chat_empty_title")}
      </h2>
      <div className="mt-8 grid w-full max-w-2xl gap-2.5 sm:grid-cols-3">
        {SUGGESTION_KEYS.map((key) => (
          <button
            key={key}
            onClick={() => onSuggestionClick(tr(key))}
            className="rounded-xl border border-border bg-card p-3.5 text-left text-sm text-foreground transition-all hover:border-primary/30 hover:bg-secondary hover:-translate-y-0.5"
            style={{ boxShadow: "var(--shadow-sm)" }}
          >
            {tr(key)}
          </button>
        ))}
      </div>
    </div>
  );
}