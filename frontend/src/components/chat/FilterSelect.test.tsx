import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FilterSelect } from "./FilterSelect";

const options = [
  { value: "All", label: "All" },
  { value: "SSM", label: "SSM" },
  { value: "KKM", label: "KKM" },
];

describe("FilterSelect", () => {
  it("shows the translated 'all' label for the All option", () => {
    render(<FilterSelect label="Authority" value="All" onChange={() => {}} options={options} allLabel="Semua" />);
    expect(screen.getByText("Semua")).toBeInTheDocument();
  });

  it("calls onChange with the newly selected value", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<FilterSelect label="Authority" value="All" onChange={onChange} options={options} allLabel="All" />);

    await user.selectOptions(screen.getByRole("combobox"), "SSM");
    expect(onChange).toHaveBeenCalledWith("SSM");
  });
});