import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ErrorBanner } from "./ErrorBanner";

describe("ErrorBanner", () => {
  it("renders nothing when there's no error", () => {
    const { container } = render(<ErrorBanner error={null} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders the error message when provided", () => {
    render(<ErrorBanner error="Something broke" />);
    expect(screen.getByText("Something broke")).toBeInTheDocument();
  });
});