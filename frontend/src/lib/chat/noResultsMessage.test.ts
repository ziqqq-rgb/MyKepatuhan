// frontend/src/lib/chat/noResultsMessage.test.ts
import { describe, it, expect } from "vitest";
import { buildNoResultsMessage } from "./noResultsMessage";

const tr = (key: string) => {
  const map: Record<string, string> = {
    filter_authority: "Authority",
    filter_topic: "Topic",
    chat_no_results_join: "and",
    chat_no_results: "No results for {filters}",
  };
  return map[key] ?? key;
};

describe("buildNoResultsMessage", () => {
  it("mentions no filters when both are All", () => {
    expect(buildNoResultsMessage(tr, "All", "All")).toBe("No results for ");
  });

  it("mentions only authority when topic is All", () => {
    expect(buildNoResultsMessage(tr, "SSM", "All")).toBe("No results for Authority: SSM");
  });

  it("mentions only topic when authority is All", () => {
    expect(buildNoResultsMessage(tr, "All", "tax")).toBe("No results for Topic: tax");
  });

  it("joins both filters when both are set", () => {
    expect(buildNoResultsMessage(tr, "SSM", "tax")).toBe(
      "No results for Authority: SSM and Topic: tax"
    );
  });
});