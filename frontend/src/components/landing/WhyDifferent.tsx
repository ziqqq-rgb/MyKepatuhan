"use client";

import { BookMarked, Quote, MapPin, RefreshCw, type LucideIcon } from "lucide-react";
import { useLanguage, type TranslationKey } from "@/lib/i18n";

type Reason = { Icon: LucideIcon; title: TranslationKey; desc: TranslationKey };

const REASONS: Reason[] = [
  { Icon: BookMarked, title: "why_1_t", desc: "why_1_d" },
  { Icon: Quote, title: "why_2_t", desc: "why_2_d" },
  { Icon: MapPin, title: "why_3_t", desc: "why_3_d" },
  { Icon: RefreshCw, title: "why_4_t", desc: "why_4_d" },
];

/**
 * Explains why answers are grounded and cited instead of guessed —
 * the differentiator from a general-purpose AI chatbot.
 */
export function WhyDifferent() {
  const { tr } = useLanguage();

  return (
    <section className="border-b border-border bg-card">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="grid gap-10 md:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] md:gap-16">
          <div className="md:sticky md:top-24 md:self-start">
            <span className="text-xs font-semibold uppercase tracking-widest text-primary">
              {tr("why_kicker")}
            </span>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
              {tr("why_title")}
            </h2>
            <p className="mt-4 text-sm leading-relaxed text-muted-foreground sm:text-base">
              {tr("why_sub")}
            </p>
          </div>

          <div className="flex flex-col divide-y divide-border overflow-hidden rounded-2xl border border-border bg-background">
            {REASONS.map(({ Icon, title, desc }) => (
              <div key={title} className="flex gap-4 p-6 transition-colors hover:bg-secondary/40">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" strokeWidth={2.25} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-foreground sm:text-base">{tr(title)}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{tr(desc)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}