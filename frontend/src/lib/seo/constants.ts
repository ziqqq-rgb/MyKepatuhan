/**
 * One place to change the site's name, canonical URL, and description.
 * Both Next's Metadata API (layout.tsx) and the JSON-LD components read
 * from here, so branding never drifts out of sync between the two.
 */
export const SITE_NAME = "MyKepatuhan";

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const SITE_DESCRIPTION =
  "AI-powered compliance assistant that turns complex Malaysian business regulations into simple, cited answers.";