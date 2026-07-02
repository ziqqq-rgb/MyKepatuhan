"use client";

import Link from "next/link";
import Image from "next/image";
import { LanguageToggle } from "@/components/LanguageToggle";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-background">

      {/* Ambient glow blobs */}
      <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div
          className="absolute -left-40 -top-40 h-[600px] w-[600px] rounded-full opacity-25 blur-[120px]"
          style={{ background: "var(--gradient-primary)" }}
        />
        <div
          className="absolute -bottom-40 -right-40 h-[500px] w-[500px] rounded-full opacity-15 blur-[120px]"
          style={{ backgroundColor: "var(--accent-2)" }}
        />
      </div>

      {/* Noise grain */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10 opacity-[0.03]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        }}
      />

      {/* Minimal header */}
      <header className="flex h-14 items-center justify-between border-b border-border/50 px-6 backdrop-blur-md">
        <Link href="/" className="flex items-center group">
          <Image src="/logo.svg" alt="MyKepatuhan logo" width={24} height={24} priority />
          <span className="text-sm font-semibold tracking-tight text-foreground">
            My<span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: "var(--gradient-primary)" }}
            >Kepatuhan</span>
          </span>
        </Link>
        <LanguageToggle />
      </header>

      {/* Content */}
      <main className="flex flex-1 items-center justify-center px-4 py-12">
        {children}
      </main>
    </div>
  );
}