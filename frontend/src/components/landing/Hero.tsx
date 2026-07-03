"use client";

import Link from "next/link";
import { Sparkles, ArrowRight, Quote } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { useLanguage } from "@/lib/i18n";

/**
 * Headline, primary CTAs, and a mock chat preview showing what an
 * answer looks like before the user signs up.
 */
export function Hero() {
  const { tr } = useLanguage();

  return (
    <section
      className="relative overflow-hidden border-b border-border"
      style={{ background: "var(--gradient-hero)" }}
    >
      <Navbar variant="landing" />

      <div
        aria-hidden
        className="pointer-events-none absolute -top-32 left-1/2 h-[480px] w-[820px] -translate-x-1/2 rounded-full opacity-50 blur-3xl"
        style={{ background: "var(--gradient-primary)" }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            "linear-gradient(to right, var(--border) 1px, transparent 1px), linear-gradient(to bottom, var(--border) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse at top, black, transparent 70%)",
        }}
      />

      <div className="relative mx-auto max-w-6xl px-4 pb-24 pt-32 sm:px-6 sm:pb-32 sm:pt-36">
        <div className="mx-auto max-w-3xl text-center">
          {/* Sized up so this reads as a tagline, not fine print */}
          <span className="inline-flex items-center gap-2 rounded-full border border-border/80 bg-card/80 px-4 py-1.5 text-sm font-semibold text-foreground shadow-sm backdrop-blur">
            <Sparkles className="h-4 w-4 text-primary" />
            {tr("hero_badge")}
          </span>

          <h1 className="mt-6 text-balance text-4xl font-semibold tracking-tight text-foreground sm:text-5xl md:text-[3.5rem]">
            {tr("hero_title").split(".").map((part, i, arr) =>
              i === arr.length - 2 ? (
                <span
                  key={i}
                  className="bg-clip-text text-transparent"
                  style={{ backgroundImage: "var(--gradient-primary)" }}
                >
                  {part}.
                </span>
              ) : (
                <span key={i}>{part}</span>
              )
            )}
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-pretty text-base leading-relaxed text-muted-foreground sm:text-lg">
            {tr("hero_sub")}
          </p>

          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/register"
              className="group inline-flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white transition-all hover:scale-[1.02] hover:opacity-95 sm:w-auto"
              style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-elegant)" }}
            >
              {tr("cta_start")}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <a
              href="#how"
              className="inline-flex w-full items-center justify-center rounded-xl border border-border bg-card/70 px-6 py-3 text-sm font-semibold text-foreground backdrop-blur transition-colors hover:bg-card sm:w-auto"
            >
              {tr("cta_how")}
            </a>
          </div>
          <p className="mt-4 text-xs text-muted-foreground">{tr("trust_line")}</p>
        </div>

        <div
          className="relative mx-auto mt-16 max-w-2xl rounded-2xl border border-border bg-card p-5 text-left"
          style={{ boxShadow: "var(--shadow-elegant)" }}
        >
          <div
            aria-hidden
            className="pointer-events-none absolute -inset-px rounded-2xl opacity-20 blur-xl"
            style={{ background: "var(--gradient-primary)" }}
          />
          <div className="relative">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-green-400/70" />
              <span className="ml-2 text-xs text-muted-foreground">MyKepatuhan · Chat</span>
            </div>
            <div className="mt-4 flex justify-end">
              <div
                className="max-w-[85%] rounded-2xl rounded-tr-md px-4 py-2.5 text-sm text-white"
                style={{ background: "var(--gradient-primary)" }}
              >
                {tr("mock_q")}
              </div>
            </div>
            <div className="mt-3 flex justify-start">
              <div className="max-w-[90%] rounded-2xl rounded-tl-md border border-border bg-secondary px-4 py-3 text-sm text-foreground">
                <div className="whitespace-pre-line leading-relaxed">{tr("mock_a")}</div>
                <div className="mt-3 flex items-center gap-1.5 border-t border-border pt-2 text-xs text-primary">
                  <Quote className="h-3 w-3" /> {tr("mock_cite")}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}