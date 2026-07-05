"use client";

import { useEffect, useState } from "react";
import { useLanguage, type TranslationKey } from "@/lib/i18n";

const STATUS_KEYS: TranslationKey[] = [
  "thinking_status_1",
  "thinking_status_2",
  "thinking_status_3",
  "thinking_status_4",
];

const ROTATE_INTERVAL_MS = 2200;

/**
 * Cycles through short status phrases while waiting for an answer.
 * Purely presentational — owns only its own rotation timer, no
 * knowledge of what the backend is actually doing.
 */
export function ThinkingIndicator() {
  const { tr } = useLanguage();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((i) => (i + 1) % STATUS_KEYS.length);
    }, ROTATE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 py-0.5 text-sm text-muted-foreground">
      <span className="flex gap-1">
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.3s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.15s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary" />
      </span>
      <span key={index} className="animate-fade-in">
        {tr(STATUS_KEYS[index])}
      </span>
    </div>
  );
}