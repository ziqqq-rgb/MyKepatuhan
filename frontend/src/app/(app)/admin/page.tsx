"use client";

import { useRef } from "react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { useLanguage } from "@/lib/i18n";
import { useRoleGate } from "@/lib/hooks/useRoleGate";
import { DocumentUploadCard } from "./DocumentUploadCard";
import { DocumentsTable, type DocumentsTableHandle } from "./DocumentsTable";

export default function AdminPage() {
  const { tr } = useLanguage();
  const user = useUser();
  const ready = useRoleGate("admin", "/chat");
  const tableRef = useRef<DocumentsTableHandle>(null);

  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <Navbar variant="app" userEmail={user?.primaryEmail ?? undefined} isAdmin />

      <main className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-foreground">{tr("admin_title")}</h1>

        <div className="mt-6">
          <DocumentUploadCard onIngestComplete={() => tableRef.current?.refresh()} />
        </div>

        <DocumentsTable ref={tableRef} />
      </main>
    </div>
  );
}