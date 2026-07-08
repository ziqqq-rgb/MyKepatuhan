import { SITE_URL } from "@/lib/seo/constants";

export type Crumb = { name: string; path: string };

/**
 * Renders BreadcrumbList structured data for one page.
 *
 * Usage (in a page component, server or client):
 *   <BreadcrumbJsonLd trail={[
 *     { name: "Home", path: "/" },
 *     { name: "Login", path: "/login" },
 *   ]} />
 *
 * `path` is site-relative ("/login"); this component joins it with
 * SITE_URL so callers never have to know the domain.
 */
export function BreadcrumbJsonLd({ trail }: { trail: Crumb[] }) {
  const json = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: trail.map(({ name, path }, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name,
      item: `${SITE_URL}${path}`,
    })),
  };

  return (
    <script
      type="application/ld+json"
      // eslint-disable-next-line react/no-danger -- static, non-user-controlled JSON
      dangerouslySetInnerHTML={{ __html: JSON.stringify(json) }}
    />
  );
}