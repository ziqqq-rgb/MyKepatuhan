import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "./StatusBadge";

const tr = (key: string) => key.replace("status_", "").toUpperCase();

describe("StatusBadge", () => {
  it.each([
    ["queued", "QUEUED"],
    ["processing", "PROCESSING"],
    ["done", "DONE"],
    ["failed", "FAILED"],
  ] as const)("renders the label for status %s", (status, expected) => {
    render(<StatusBadge status={status} tr={tr} />);
    expect(screen.getByText(expected)).toBeInTheDocument();
  });
});