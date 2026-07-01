"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import { useLanguage } from "@/lib/i18n";
import type { AssistantMessage } from "./constants";

// Tailwind styling for each Markdown element, kept in one place so the
// visual language of assistant answers stays consistent.
const markdownComponents = {
  p: ({ children }: any) => <p className="my-2 leading-relaxed">{children}</p>,
  strong: ({ children }: any) => (
    <strong className="font-semibold text-foreground">{children}</strong>
  ),
  em: ({ children }: any) => <em className="italic">{children}</em>,
  ul: ({ children }: any) => (
    <ul className="my-2 ml-4 list-disc space-y-1 marker:text-primary">{children}</ul>
  ),
  ol: ({ children }: any) => (
    <ol className="my-2 ml-4 list-decimal space-y-1 marker:text-primary marker:font-medium">
      {children}
    </ol>
  ),
  li: ({ children }: any) => <li className="pl-1">{children}</li>,
  h1: ({ children }: any) => (
    <h1 className="mt-3 mb-1.5 text-base font-semibold text-foreground">{children}</h1>
  ),
  h2: ({ children }: any) => (
    <h2 className="mt-3 mb-1.5 text-sm font-semibold text-foreground">{children}</h2>
  ),
  h3: ({ children }: any) => (
    <h3 className="mt-2.5 mb-1 text-sm font-semibold text-foreground">{children}</h3>
  ),
  a: ({ children, href }: any) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary underline underline-offset-2 hover:text-primary/80"
    >
      {children}
    </a>
  ),
  code: ({ children }: any) => (
    <code className="rounded bg-secondary px-1.5 py-0.5 font-mono text-xs text-foreground">
      {children}
    </code>
  ),
  blockquote: ({ children }: any) => (
    <blockquote className="my-2 border-l-2 border-primary/40 pl-3 text-muted-foreground">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-3 border-border" />,
  table: ({ children }: any) => (
    <div className="my-2 overflow-x-auto">
      <table className="w-full border-collapse text-xs">{children}</table>
    </div>
  ),
  th: ({ children }: any) => (
    <th className="border-b border-border px-2 py-1.5 text-left font-semibold text-foreground">
      {children}
    </th>
  ),
  td: ({ children }: any) => (
    <td className="border-b border-border px-2 py-1.5 text-muted-foreground">{children}</td>
  ),
};

export function AssistantBubble({ message }: { message: AssistantMessage }) {
  const { tr } = useLanguage();
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const citationCount = message.citations?.length ?? 0;

  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] rounded-2xl rounded-tl-md border border-border bg-card px-4 py-3.5 text-sm text-foreground">
        <div className="leading-relaxed [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {message.content}
          </ReactMarkdown>
        </div>

        {citationCount > 0 && (
          <div className="mt-3 border-t border-border pt-3">
            <button
              onClick={() => setSourcesOpen((o) => !o)}
              className="text-xs font-medium text-primary hover:underline"
            >
              {sourcesOpen ? tr("chat_hide_sources") : tr("chat_show_sources")} ({citationCount})
            </button>
            {sourcesOpen && (
              <div className="mt-3 space-y-2">
                {message.citations!.map((c, i) => (
                  <div key={i} className="rounded-xl bg-secondary p-3 text-xs">
                    <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                      <span className="font-semibold text-foreground">{c.document_title}</span>
                      <span className="ml-auto font-mono text-muted-foreground">
                        {c.score.toFixed(2)}
                      </span>
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