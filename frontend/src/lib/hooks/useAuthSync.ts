"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useUser } from "@stackframe/stack";
import { getToken, setToken, apiOAuthLogin } from "@/lib/api";

const MAX_TOKEN_POLL_ATTEMPTS = 5;
const TOKEN_POLL_INTERVAL_MS = 300;

/** Stack's access token can be briefly unavailable right after sign-in
 * while the session finishes initializing — poll for it a few times. */
async function waitForStackAccessToken(user: { getAuthJson: () => Promise<{ accessToken: string | null }> }) {
  for (let attempt = 0; attempt < MAX_TOKEN_POLL_ATTEMPTS; attempt++) {
    const { accessToken } = await user.getAuthJson();
    if (accessToken) return accessToken;
    await new Promise((resolve) => setTimeout(resolve, TOKEN_POLL_INTERVAL_MS));
  }
  throw new Error("No access token available from Stack session");
}

/**
 * Bridges Stack Auth (frontend session) with our FastAPI backend (JWT).
 * On first load after a Stack sign-in there's a Stack session but no
 * backend JWT yet — this exchanges one for the other, once.
 * Redirects to /login if there's no Stack session or the exchange fails.
 */
export function useAuthSync() {
  const router = useRouter();
  const pathname = usePathname(); // re-check on route change, same as before
  const user = useUser();
  const [isReady, setIsReady] = useState(false);
  const syncInFlight = useRef(false);

  useEffect(() => {
    if (user === null) {
      router.replace("/login");
      return;
    }

    if (getToken()) {
      setIsReady(true);
      return;
    }

    if (syncInFlight.current) return;
    syncInFlight.current = true;

    (async () => {
      try {
        const accessToken = await waitForStackAccessToken(user);
        const res = await apiOAuthLogin(accessToken);
        setToken(res.access_token);
        setIsReady(true);
      } catch (err) {
        console.error("Failed to sync OAuth with backend:", err);
        router.replace("/login");
      } finally {
        syncInFlight.current = false;
      }
    })();
  }, [user, router, pathname]);

  return isReady;
}