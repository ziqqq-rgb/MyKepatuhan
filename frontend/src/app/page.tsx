"use client";

import Link from "next/link";
import {
  FileUp, MessagesSquare, ListChecks,
  Briefcase, UtensilsCrossed, User,
  Sparkles, ArrowRight, ShieldCheck, Quote,
} from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { useLanguage } from "@/lib/i18n";

const AUTHORITIES = ["SSM", "KKM", "DBKL", "MPKj", "LHDN", "MBPJ", "JAKIM"];

export default function HomePage() {
  const { tr } = useLanguage();

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* ── Hero (relative wrapper so the floating navbar has something to sit on) ── */}
      <section
        className="relative overflow-hidden border-b border-border"
        style={{ background: "var(--gradient-hero)" }}
      >
        <Navbar variant="landing" />

        {/* Glow orb */}
        <div
          aria-hidden
          className="pointer-events-none absolute -top-32 left-1/2 h-[480px] w-[820px] -translate-x-1/2 rounded-full opacity-50 blur-3xl"
          style={{ background: "var(--gradient-primary)" }}
        />
        {/* Grid */}
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
            {/* Badge */}
            <span className="inline-flex items-center gap-2 rounded-full border border-border/80 bg-card/80 px-3 py-1 text-xs font-medium text-foreground shadow-sm backdrop-blur">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              {tr("hero_badge")}
            </span>

            {/* Headline */}
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

            {/* CTAs */}
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

          {/* Chat mockup */}
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
              {/* Fake window chrome */}
              <div className="flex items-center gap-2 border-b border-border pb-3">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-green-400/70" />
                <span className="ml-2 text-xs text-muted-foreground">MyKepatuhan · Chat</span>
              </div>
              {/* User bubble */}
              <div className="mt-4 flex justify-end">
                <div
                  className="max-w-[85%] rounded-2xl rounded-tr-md px-4 py-2.5 text-sm text-white"
                  style={{ background: "var(--gradient-primary)" }}
                >
                  {tr("mock_q")}
                </div>
              </div>
              {/* Assistant bubble */}
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

      {/* ── Stats strip ── */}
      <section className="border-b border-border bg-card">
        <div className="mx-auto grid max-w-5xl grid-cols-3 divide-x divide-border px-4 sm:px-6">
          {([
            { v: "1,200+", k: "stat_docs" as const },
            { v: "7", k: "stat_authorities" as const },
            { v: "24/7", k: "stat_answers" as const },
          ]).map(({ v, k }) => (
            <div key={k} className="px-2 py-10 text-center">
              <div
                className="bg-clip-text text-3xl font-bold tracking-tight text-transparent sm:text-4xl"
                style={{ backgroundImage: "var(--gradient-primary)" }}
              >
                {v}
              </div>
              <div className="mt-1 text-xs text-muted-foreground sm:text-sm">{tr(k)}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how" className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {tr("how_title")}
          </h2>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {([
              { Icon: FileUp, key: "how_1" as const },
              { Icon: MessagesSquare, key: "how_2" as const },
              { Icon: ListChecks, key: "how_3" as const },
            ]).map(({ Icon, key }, i) => (
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

      {/* ── Who for ── */}
      <section className="relative border-b border-border bg-card">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            background:
              "radial-gradient(circle at 15% 50%, color-mix(in oklab, var(--primary-glow) 12%, transparent), transparent 50%), radial-gradient(circle at 85% 50%, color-mix(in oklab, var(--accent-2) 10%, transparent), transparent 50%)",
          }}
        />
        <div className="relative mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {tr("who_title")}
          </h2>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {([
              { Icon: Briefcase, t: "who_1_t" as const, d: "who_1_d" as const },
              { Icon: UtensilsCrossed, t: "who_2_t" as const, d: "who_2_d" as const },
              { Icon: User, t: "who_3_t" as const, d: "who_3_d" as const },
            ]).map(({ Icon, t: tKey, d }) => (
              <div
                key={tKey}
                className="rounded-2xl border border-border bg-background p-6 transition-all hover:shadow-md"
                style={{ background: "var(--gradient-card)" }}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" strokeWidth={2.25} />
                </div>
                <h3 className="mt-4 text-base font-semibold text-foreground">{tr(tKey)}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{tr(d)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Authorities ── */}
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

      {/* ── CTA banner ── */}
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

      <Footer />
    </div>
  );
}