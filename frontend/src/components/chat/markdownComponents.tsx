import type { Components } from "react-markdown";

/**
 * Maps markdown elements to styled components for assistant replies.
 * Pure presentation config — kept out of AssistantBubble so that file
 * stays focused on the citations UI/state.
 */
export const chatMarkdownComponents: Components = {
  p: ({ children }) => <p className="my-2 leading-relaxed">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  ul: ({ children }) => <ul className="my-2 ml-4 list-disc space-y-1 marker:text-primary">{children}</ul>,
  ol: ({ children }) => (
    <ol className="my-2 ml-4 list-decimal space-y-1 marker:text-primary marker:font-medium">{children}</ol>
  ),
  li: ({ children }) => <li className="pl-1">{children}</li>,
  h1: ({ children }) => <h1 className="mt-3 mb-1.5 text-base font-semibold text-foreground">{children}</h1>,
  h2: ({ children }) => <h2 className="mt-3 mb-1.5 text-sm font-semibold text-foreground">{children}</h2>,
  h3: ({ children }) => <h3 className="mt-2.5 mb-1 text-sm font-semibold text-foreground">{children}</h3>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2 hover:text-primary/80">
      {children}
    </a>
  ),
  code: ({ children }) => (
    <code className="rounded bg-secondary px-1.5 py-0.5 font-mono text-xs text-foreground">{children}</code>
  ),
  blockquote: ({ children }) => (
    <blockquote className="my-2 border-l-2 border-primary/40 pl-3 text-muted-foreground">{children}</blockquote>
  ),
  hr: () => <hr className="my-3 border-border" />,
  table: ({ children }) => (
    <div className="my-2 overflow-x-auto">
      <table className="w-full border-collapse text-xs">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border-b border-border px-2 py-1.5 text-left font-semibold text-foreground">{children}</th>
  ),
  td: ({ children }) => <td className="border-b border-border px-2 py-1.5 text-muted-foreground">{children}</td>,
};