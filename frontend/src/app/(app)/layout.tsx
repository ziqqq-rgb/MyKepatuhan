"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useUser } from "@stackframe/stack";
import { getToken, setToken, apiOAuthLogin } from "@/lib/api";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useUser();
  const [isReady, setIsReady] = useState(false);
  const syncInFlight = useRef(false);

  useEffect(() => {
    if (user === null) {
      router.replace("/login");
      return;
    }

  const token = getToken();

  if (user && !token) {
    if (syncInFlight.current) return;
    syncInFlight.current = true;

    (async () => {
      try {
        let accessToken: string | null = null;
        for (let i = 0; i < 5 && !accessToken; i++) {
          const authJson = await user.getAuthJson();
          accessToken = authJson.accessToken;
          if (!accessToken) await new Promise(r => setTimeout(r, 300));
        }
        if (!accessToken) throw new Error("No access token available from Stack session");

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
    return;
  }

    setIsReady(true);
  }, [user, router, pathname]);

  if (!isReady) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}