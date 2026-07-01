"use client";

import { useEffect, useRef } from "react";
import { ArrowUp } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { AUTHORITIES, TOPICS } from "./constants";
import { FilterSelect } from "./FilterSelect";

type ChatInputProps = {
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  authority: string;
  onAuthorityChange: (value: string) => void;
  topic: string;
  onTopicChange: (value: string) => void;
  loading: boolean;
};

export function ChatInput({
  input,
  onInputChange,
  onSend,
  authority,
  onAuthorityChange,
  topic,
  onTopicChange,
  loading,
}: ChatInputProps) {
  const { tr } = useLanguage();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Grow the textarea with content, capped at 140px, same as before.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 140) + "px";
  }, [input]);

  return (
    <div className="border-t border-border bg-card">
      <div className="mx-auto w-full max-w-3xl px-4 py-3">
        <div className="rounded-2xl border border-border bg-background p-2 transition-colors focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/10">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
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
                onChange={onAuthorityChange}
                options={AUTHORITIES}
                allLabel={tr("filter_all")}
              />
              <FilterSelect
                label={tr("filter_topic")}
                value={topic}
                onChange={onTopicChange}
                options={TOPICS}
                allLabel={tr("filter_all")}
              />
            </div>
            <button
              onClick={onSend}
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
  );
}