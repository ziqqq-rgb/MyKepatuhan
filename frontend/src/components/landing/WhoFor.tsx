"use client";

import { useLanguage, type TranslationKey } from "@/lib/i18n";

const AUDIENCES: { title: TranslationKey; desc: TranslationKey }[] = [
  { title: "who_1_t", desc: "who_1_d" },
  { title: "who_2_t", desc: "who_2_d" },
  { title: "who_3_t", desc: "who_3_d" },
];

export function WhoFor() {
  const { tr } = useLanguage();

  return (
    <section className="relative border-b border-border bg-card">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          background:
            "radial-gradient(circle at 15% 50%, color-mix(in oklab, var(--primary-glow) 12%, transparent), transparent 50%), radial-gradient(circle at 85% 50%, color-mix(in oklab, var(--accent-2) 10%, transparent), transparent 50%)",
        }}
      />
      <div className="relative mx-auto max-w-4xl px-4 py-20 sm:px-6">
        <h2 className="text-center text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {tr("who_title")}
        </h2>

        <div className="mt-14 overflow-hidden rounded-2xl border border-border">
          <div className="divide-y divide-border">
            {AUDIENCES.map(({ title, desc }, i) => (
              <div
                key={title}
                className="group flex flex-col gap-4 bg-background p-6 transition-colors hover:bg-secondary/40 sm:flex-row sm:items-center sm:gap-6 sm:p-8"
              >
                <span
                  aria-hidden
                  className="text-4xl font-bold text-border transition-colors group-hover:text-primary/30 sm:text-5xl"
                >
                  0{i + 1}
                </span>
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-foreground">{tr(title)}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{tr(desc)}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-border bg-secondary/40 px-6 py-4 text-center text-sm text-muted-foreground sm:px-8">
            {tr("who_more")}
          </div>
        </div>
      </div>
    </section>
  );
}
