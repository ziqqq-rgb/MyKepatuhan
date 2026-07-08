import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/seo/constants";

/**
 * /chat, /admin, and /handler are behind auth and have no value as
 * search results — keep crawlers off them so index quality (and
 * crawl budget) isn't spent on pages nobody can open without logging in.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/chat", "/admin", "/handler"],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
