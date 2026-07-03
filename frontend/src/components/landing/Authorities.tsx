"use client";

import { useLanguage } from "@/lib/i18n";

const AUTHORITIES = ["SSM", "KKM", "DBKL", "MPKj", "LHDN", "MBPJ", "JAKIM"];

export function Authorities() {
  const { tr } = useLanguage();

  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-5xl px-4 py-20 text-center sm:px-6">
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {tr("auth_title")}
        </h2>
        <div className="mt-10 flex flex-wrap justify-center gap-2.5">
          {AUTHORITIES.map((a) => (
            <span
              key={a}
              className="rounded-full border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground shadow-sm transition-all hover:-translate-y-0.5 hover:border-primary/40 hover:text-primary"
            >
              {a}
            </span>
          ))}
          <span className="rounded-full border border-dashed border-border bg-card px-4 py-2 text-sm text-muted-foreground">
            + more
          </span>
        </div>
        <p className="mt-6 text-sm text-muted-foreground">{tr("auth_note")}</p>
      </div>
    </section>
  );
}