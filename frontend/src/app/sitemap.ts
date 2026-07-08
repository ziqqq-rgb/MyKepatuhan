import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/seo/constants";

export default function sitemap(): MetadataRoute.Sitemap {
  const publicPaths = ["/", "/login", "/register"];

  return publicPaths.map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: new Date(),
  }));
}
