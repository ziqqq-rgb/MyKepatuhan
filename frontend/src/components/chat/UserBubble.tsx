"use client";

import type { UserMessage } from "./constants";

export function UserBubble({ message }: { message: UserMessage }) {
  return (
    <div className="flex justify-end">
      <div
        className="max-w-[80%] rounded-2xl rounded-tr-md px-4 py-2.5 text-sm leading-relaxed text-white"
        style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-sm)" }}
      >
        {message.content}
      </div>
    </div>
  );
}