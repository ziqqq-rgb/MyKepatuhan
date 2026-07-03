"use client";

import { useAuthSync } from "@/lib/hooks/useAuthSync";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const isReady = useAuthSync();

  if (!isReady) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}