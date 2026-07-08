import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n";
import { StackProvider } from "@stackframe/stack";
import { stackApp } from "@/lib/stack";
import { WebsiteJsonLd } from "@/components/seo/WebsiteJsonLd";
import { SITE_NAME, SITE_URL, SITE_DESCRIPTION } from "@/lib/seo/constants";

export const metadata: Metadata = {
  // Required so relative OG image / icon URLs resolve to an absolute URL.
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} — Malaysian Business Compliance Assistant`,
    // Subpages that set their own title (e.g. "Login") render as "Login | MyKepatuhan".
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  openGraph: {
    siteName: SITE_NAME,
    title: `${SITE_NAME} — Malaysian Business Compliance Assistant`,
    description: SITE_DESCRIPTION,
    url: SITE_URL,
    type: "website",
  },
  // favicon.ico, icon.svg, and apple-icon.png in this same app/ folder are
  // picked up automatically by Next's file-based metadata convention —
  // no manual <link rel="icon"> tags needed.
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <WebsiteJsonLd />
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
