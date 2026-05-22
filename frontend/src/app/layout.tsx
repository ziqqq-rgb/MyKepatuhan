import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n";
import { StackProvider } from "@stackframe/stack";
import { stackApp } from "@/lib/stack";

export const metadata: Metadata = {
  title: "MyKepatuhan — Malaysian Business Compliance Assistant",
  description:
    "AI-powered compliance assistant that turns complex Malaysian business regulations into simple, cited answers.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <StackProvider app={stackApp}>
          <LanguageProvider>
            <Suspense
              fallback={
                <div className="flex h-screen items-center justify-center bg-background">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
                </div>
              }
            >
              {children}
            </Suspense>
          </LanguageProvider>
        </StackProvider>
      </body>
    </html>
  );
}