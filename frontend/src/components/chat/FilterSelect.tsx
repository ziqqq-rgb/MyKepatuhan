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
    <label className="flex items-center gap-1 rounded-full border border-border bg-secondary/60 px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:border-primary/30">
      <span className="hidden sm:inline">{label}:</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-transparent text-foreground focus:outline-none"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value} className="bg-card text-foreground">
            {o.value === "All" ? allLabel : o.label}
          </option>
        ))}
      </select>
    </label>
  );
}