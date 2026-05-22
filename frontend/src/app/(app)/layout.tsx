"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@stackframe/stack";
import { getToken } from "@/lib/api";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router  = useRouter();
  const user    = useUser();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (user === null) { router.replace("/login"); return; }
    if (user !== undefined && !getToken()) { router.replace("/login"); return; }
    if (user !== undefined) setReady(true);
  }, [user, router]);

  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
  }

  return <>{children}</>;
}