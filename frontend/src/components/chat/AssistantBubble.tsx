"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { chatMarkdownComponents } from "./markdownComponents";
import type { AssistantMessage } from "./constants";

export function AssistantBubble({ message }: { message: AssistantMessage }) {
  const { tr } = useLanguage();
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const citationCount = message.citations?.length ?? 0;

  return (
    <div className="flex items-start gap-2.5">
      <div
        className="max-w-[90%] rounded-2xl rounded-tl-md border border-border bg-card px-4 py-3.5 text-sm text-foreground"
        style={{ boxShadow: "var(--shadow-sm)" }}
      >
        <div className="leading-relaxed [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={chatMarkdownComponents}>
            {message.content}
          </ReactMarkdown>
        </div>

        {citationCount > 0 && (
          <div className="mt-3 border-t border-border pt-3">
            <button
              onClick={() => setSourcesOpen((o) => !o)}
              className="flex items-center gap-1 text-xs font-medium text-primary hover:text-primary/80"
            >
              {sourcesOpen ? tr("chat_hide_sources") : tr("chat_show_sources")} ({citationCount})
              <ChevronDown className={`h-3 w-3 transition-transform ${sourcesOpen ? "rotate-180" : ""}`} />
            </button>
            {sourcesOpen && (
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