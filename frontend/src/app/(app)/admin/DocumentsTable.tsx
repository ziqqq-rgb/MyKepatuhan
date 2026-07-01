"use client";

import { useEffect, useImperativeHandle, useState, forwardRef } from "react";
import { FileText } from "lucide-react";
import { ErrorBanner } from "@/components/ErrorBanner";
import { useLanguage } from "@/lib/i18n";
import { apiGetDocuments, type IngestedDocument } from "@/lib/api";

export type DocumentsTableHandle = { refresh: () => void };

export const DocumentsTable = forwardRef<DocumentsTableHandle>(function DocumentsTable(_, ref) {
  const { tr, lang } = useLanguage();
  const [docs, setDocs] = useState<IngestedDocument[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      const list = await apiGetDocuments();
      setDocs(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents");
      setDocs([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  useImperativeHandle(ref, () => ({ refresh: load }));

  return (
    <section className="mt-10">
      <h2 className="text-lg font-semibold text-foreground">{tr("admin_ingested")}</h2>
      <div className="mt-4 overflow-hidden rounded-2xl border border-border bg-card">
        {docs === null ? (
          <div className="flex items-center justify-center p-10">
            <div className="h-7 w-7 animate-spin rounded-full border-2 border-border border-t-primary" />
          </div>
        ) : error ? (
          <div className="p-4"><ErrorBanner error={error} /></div>
        ) : docs.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-center text-sm text-muted-foreground">
            <FileText className="h-7 w-7" strokeWidth={1.5} />
            <p className="mt-3">{tr("admin_empty")}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-secondary/50 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  <th className="px-4 py-3">{tr("admin_col_name")}</th>
                  <th className="px-4 py-3">{tr("admin_col_file")}</th>
                  <th className="px-4 py-3">{tr("admin_col_at")}</th>
                  <th className="px-4 py-3">{tr("admin_col_hash")}</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((d, i) => (
                  <tr key={i} className="border-b border-border last:border-b-0 hover:bg-secondary/40 transition-colors">
                    <td className="px-4 py-3 font-medium text-foreground">{d.doc_name ?? "—"}</td>
                    <td className="px-4 py-3 text-muted-foreground">{d.filename ?? "—"}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {d.ingested_at
                        ? new Date(d.ingested_at).toLocaleString(lang === "bm" ? "ms-MY" : "en-MY")
                        : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{d.hash}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
});