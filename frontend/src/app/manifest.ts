import type { MetadataRoute } from "next";
import { SITE_NAME } from "@/lib/seo/constants";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: SITE_NAME,
    short_name: SITE_NAME,
    description: "Malaysian business compliance assistant",
    start_url: "/",
    display: "standalone",
    background_color: "#0d0e15",
    theme_color: "#7B1FA2",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
