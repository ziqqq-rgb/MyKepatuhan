import { SITE_NAME, SITE_URL } from "@/lib/seo/constants";

/**
 * Tells Google what to call this site in search results (the text next
 * to the favicon). Rendered once in the root layout so it's present on
 * every page. No props needed — it's sitewide, not per-page data.
 */
export function WebsiteJsonLd() {
  const json = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: SITE_NAME,
    url: SITE_URL,
  };

  return (
    <script
      type="application/ld+json"
      // eslint-disable-next-line react/no-danger -- static, non-user-controlled JSON
      dangerouslySetInnerHTML={{ __html: JSON.stringify(json) }}
    />
  );
}