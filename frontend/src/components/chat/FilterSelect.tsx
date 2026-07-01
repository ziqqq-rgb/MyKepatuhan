"use client";

import type { FilterOption } from "./constants";

type FilterSelectProps = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: FilterOption[];
  allLabel: string;
};

export function FilterSelect({ label, value, onChange, options, allLabel }: FilterSelectProps) {
  return (
    <label className="flex items-center gap-1 rounded-md border border-border bg-card px-2 py-1 text-xs text-muted-foreground">
      <span className="hidden sm:inline">{label}:</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-transparent text-foreground focus:outline-none"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.value === "All" ? allLabel : o.label}
          </option>
        ))}
      </select>
    </label>
  );
}