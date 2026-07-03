"use client";

import { useLanguage } from "@/lib/i18n";

const AUTHORITIES = ["SSM", "KKM", "DBKL", "MPKj", "LHDN", "MBPJ", "JAKIM", "+ more"];
const LOOPED = [...AUTHORITIES, ...AUTHORITIES];

export function Authorities() {
  const { tr } = useLanguage();

  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-5xl px-4 py-20 text-center sm:px-6">
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {tr("auth_title")}
        </h2>

        <div
          className="mt-10 overflow-hidden"
          style={{
            maskImage:
              "linear-gradient(to right, transparent, black 8%, black 92%, transparent)",
            WebkitMaskImage:
              "linear-gradient(to right, transparent, black 8%, black 92%, transparent)",
          }}
        >
          <div className="animate-marquee flex w-max gap-8">
            {LOOPED.map((a, i) => {
              const isMore = a === "+ more";
              return (
                <span
                  key={`${a}-${i}`}
                  className={`shrink-0 rounded-full border px-6 py-4 text-sm font-semibold shadow-sm transition-all ${
                    isMore
                      ? "border-dashed border-border bg-card font-normal text-muted-foreground shadow-none"
                      : "border-border bg-card text-foreground hover:-translate-y-0.5 hover:border-primary/40 hover:text-primary"
                  }`}
                >
                  {a}
                </span>
              );
            })}
          </div>
        </div>

        <p className="mt-6 text-sm text-muted-foreground">{tr("auth_note")}</p>
      </div>
    </section>
  );
}