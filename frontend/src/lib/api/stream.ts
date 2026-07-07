/**
 * Parses a fetch Response body as Server-Sent Events.
 *
 * Usage:
 *   const res = await apiQueryStream(question);
 *   for await (const { event, data } of readSseStream<MyEventData>(res)) { ... }
 */
export interface SseMessage<T> {
  event: string;
  data: T;
}

export async function* readSseStream<T>(response: Response): AsyncGenerator<SseMessage<T>> {
  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE blocks are separated by a blank line.
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const message = parseSseBlock<T>(buffer.slice(0, boundary));
      if (message) yield message;
      buffer = buffer.slice(boundary + 2);
      boundary = buffer.indexOf("\n\n");
    }
  }
}

function parseSseBlock<T>(block: string): SseMessage<T> | null {
  let event = "message";
  const dataLines: string[] = [];

  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }

  if (dataLines.length === 0) return null;
  return { event, data: JSON.parse(dataLines.join("\n")) as T };
}