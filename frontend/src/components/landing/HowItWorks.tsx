"use client";

import { FileUp, MessagesSquare, ListChecks, type LucideIcon } from "lucide-react";
import { useLanguage, type TranslationKey } from "@/lib/i18n";

const STEPS: { Icon: LucideIcon; key: TranslationKey }[] = [
  { Icon: FileUp, key: "how_1" },
  { Icon: MessagesSquare, key: "how_2" },
  { Icon: ListChecks, key: "how_3" },
];

export function HowItWorks() {
  const { tr } = useLanguage();

  return (
    <section id="how" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <h2 className="text-center text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {tr("how_title")}
        </h2>
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {STEPS.map(({ Icon, key }, i) => (
            <div
              key={key}
              className="group relative overflow-hidden rounded-2xl border border-border bg-card p-6 transition-all hover:-translate-y-1 hover:border-primary/40 hover:shadow-lg"
            >
              <div
                aria-hidden
                className="absolute -right-10 -top-10 h-32 w-32 rounded-full opacity-0 blur-2xl transition-opacity group-hover:opacity-40"
                style={{ background: "var(--gradient-primary)" }}
              />
              <div className="relative">
                <div
                  className="flex h-12 w-12 items-center justify-center rounded-xl text-white"
                  style={{ background: "var(--gradient-primary)" }}
                >
                  <Icon className="h-5 w-5" strokeWidth={2.25} />
                </div>
                <div className="mt-5 text-xs font-semibold uppercase tracking-widest text-primary">
                  Step 0{i + 1}
                </div>
                <p className="mt-2 text-lg font-medium leading-snug text-foreground">
                  {tr(key)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}