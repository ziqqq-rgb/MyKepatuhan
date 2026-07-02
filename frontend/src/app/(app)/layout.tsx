"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useUser } from "@stackframe/stack";
import { getToken, setToken, apiOAuthLogin } from "@/lib/api";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useUser();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (user === null) {
      router.replace("/login");
      return;
    }

    const token = getToken();

    if (user && !token) {
      // Stack owns the session; we only need its access token to mint
      // our own backend JWT once, right after sign-in.
      user
        .getAuthJson()
        .then(({ accessToken }) => apiOAuthLogin(accessToken))
        .then((res) => {
          setToken(res.access_token);
          setIsReady(true);
        })
        .catch((err) => {
          console.error("Failed to sync OAuth with backend:", err);
          router.replace("/login");
        });
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