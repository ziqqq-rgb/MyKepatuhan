"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGetMe } from "@/lib/api";

type Role = "admin" | "user";

export function useRoleGate(requiredRole: Role, redirectTo: string) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    apiGetMe()
      .then((me) => {
        const hasAccess = requiredRole === "admin" ? me.is_admin : !me.is_admin;
        if (hasAccess) {
          setReady(true);
        } else {
          router.replace(redirectTo);
        }
      })
      .catch(() => router.replace("/login"));
  }, [requiredRole, redirectTo, router]);

  return ready;
}