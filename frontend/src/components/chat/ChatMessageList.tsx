"use client";

import { UserBubble } from "./UserBubble";
import { AssistantBubble } from "./AssistantBubble";
import type { Message } from "./constants";

type ChatMessageListProps = {
  messages: Message[];
  sending: boolean;
};

function isLastAssistant(message: Message, index: number, messages: Message[]): boolean {
  return index === messages.length - 1 && message.role === "assistant";
}

/** No tokens yet — show the thinking indicator. */
function isPending(message: Message, index: number, messages: Message[], sending: boolean): boolean {
  return sending && isLastAssistant(message, index, messages) && message.content === "";
}

/** Tokens are actively arriving — show word-by-word fade-in. */
function isStreaming(message: Message, index: number, messages: Message[], sending: boolean): boolean {
  return sending && isLastAssistant(message, index, messages) && message.content !== "";
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
            isStreaming={isStreaming(message, index, messages, sending)}
          />
        )
      )}
    </div>
  );
}