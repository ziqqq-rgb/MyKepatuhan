"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldAlert } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { useLanguage } from "@/lib/i18n";
import { apiGetMe } from "@/lib/api";
import { DocumentUploadCard } from "@/components/admin/DocumentUploadCard";
import { DocumentsTable, type DocumentsTableHandle } from "@/components/admin/DocumentsTable";

export default function AdminPage() {
  const { tr } = useLanguage();
  const user = useUser();
  const router = useRouter();

  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const documentsTableRef = useRef<DocumentsTableHandle>(null);

  useEffect(() => {
    apiGetMe()
      .then((me) => {
        if (!me.is_admin) {
          router.replace("/chat");
        } else {
          setIsAdmin(true);
        }
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  if (isAdmin === null) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar variant="app" userEmail={user?.primaryEmail ?? undefined} isAdmin />

      <main className="mx-auto w-full max-w-4xl px-4 py-10 sm:px-6">
        <div className="mb-8 flex items-center gap-3">
          <div
            className="flex h-10 w-10 items-center justify-center rounded-xl text-white"
            style={{ background: "var(--gradient-primary)" }}
          >
            <ShieldAlert className="h-5 w-5" strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-foreground">{tr("admin_title")}</h1>
            <p className="text-sm text-muted-foreground">Admin access only</p>
          </div>
        </div>

        <DocumentUploadCard onIngestComplete={() => documentsTableRef.current?.refresh()} />
        <DocumentsTable ref={documentsTableRef} />
      </main>
    </div>
  );
}