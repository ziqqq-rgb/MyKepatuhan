"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { useLanguage } from "@/lib/i18n";
import { apiGetMe } from "@/lib/api";
import { DocumentUploadCard } from "./DocumentUploadCard";
import { DocumentsTable, type DocumentsTableHandle } from "./DocumentsTable";

export default function AdminPage() {
  const { tr } = useLanguage();
  const user = useUser();
  const router = useRouter();
  const [accessChecked, setAccessChecked] = useState(false);
  const tableRef = useRef<DocumentsTableHandle>(null);

  // Only admins are allowed here — everyone else gets redirected to /chat.
  useEffect(() => {
    apiGetMe()
      .then((me) => {
        if (me.is_admin) {
          setAccessChecked(true);
        } else {
          router.replace("/chat");
        }
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  if (!accessChecked) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <Navbar variant="app" userEmail={user?.primaryEmail ?? undefined} isAdmin />

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            {tr("admin_title")}
          </h1>

          <div className="mt-6">
            <DocumentUploadCard onIngestComplete={() => tableRef.current?.refresh()} />
          </div>

          <DocumentsTable ref={tableRef} />
        </div>
      </main>
    </div>
  );
}