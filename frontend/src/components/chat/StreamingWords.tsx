"use client";

import { useEffect, useRef, useState } from "react";

const REVEAL_INTERVAL_MS = 35; // time between each newly revealed word

type StreamingWordsProps = { text: string };


export function StreamingWords({ text }: StreamingWordsProps) {
  const tokensRef = useRef<string[]>([]);
  const [revealedCount, setRevealedCount] = useState(0);

  useEffect(() => {
    tokensRef.current = text.split(/(\s+)/);
  }, [text]);

  useEffect(() => {
    const id = setInterval(() => {
      setRevealedCount((count) =>
        count < tokensRef.current.length ? count + 1 : count
      );
    }, REVEAL_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  const visible = tokensRef.current.slice(0, revealedCount);

  return (
    <span className="whitespace-pre-wrap">
      {visible.map((token, i) => (

        <span key={i} className="inline-block animate-word-in">
          {token}
        </span>
      ))}
    </span>
  );
}