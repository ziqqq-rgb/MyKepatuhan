"use client";

import Link from "next/link";
import { ShieldCheck, ArrowRight } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export function CtaBanner() {
  const { tr } = useLanguage();

  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6">
        <div
          className="relative overflow-hidden rounded-3xl px-8 py-14 text-center text-white sm:px-12"
          style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-elegant)" }}
        >
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 opacity-20"
            style={{
              backgroundImage: "radial-gradient(white 1px, transparent 1px)",
              backgroundSize: "24px 24px",
            }}
          />
          <div className="relative">
            <ShieldCheck className="mx-auto h-10 w-10" strokeWidth={2} />
            <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
              {tr("cta_start")}
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-sm opacity-90 sm:text-base">
              {tr("trust_line")}
            </p>
            <Link
              href="/register"
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-semibold text-primary transition-transform hover:scale-105"
            >
              {tr("nav_get_started")}
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}