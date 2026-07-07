"use client";

import { UserBubble } from "./UserBubble";
import { AssistantBubble } from "./AssistantBubble";
import type { Message } from "./constants";

type ChatMessageListProps = {
  messages: Message[];
  /** True while an answer is still streaming in — used to show the typing indicator on the in-progress message. */
  sending: boolean;
};

/**
 * A message is "pending" only if it's the last one, belongs to the
 * assistant, has no content yet, and streaming is still in flight —
 * i.e. the placeholder bubble created right before the first token arrives.
 */
function isPending(message: Message, index: number, messages: Message[], sending: boolean): boolean {
  return sending && index === messages.length - 1 && message.role === "assistant" && message.content === "";
}

export function ChatMessageList({ messages, sending }: ChatMessageListProps) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-6">
      {messages.map((message, index) =>
        message.role === "user" ? (
          <UserBubble key={message.id} message={message} />
        ) : (
          <AssistantBubble
            key={message.id}
            message={message}
            isPending={isPending(message, index, messages, sending)}
          />
        )
      )}
    </div>
  );
}