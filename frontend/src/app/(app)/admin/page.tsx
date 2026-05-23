"use client";

import { useEffect, useRef, useState } from "react";
import { UploadCloud, FileText, ShieldAlert } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { Navbar } from "@/components/Navbar";
import { ErrorBanner } from "@/components/ErrorBanner";
import { useLanguage } from "@/lib/i18n";
import {
  apiUploadDocument,
  apiGetJobStatus,
  apiGetDocuments,
  apiGetMe,
  type IngestJob,
  type IngestedDocument,
} from "@/lib/api";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const { tr, lang } = useLanguage();
  const user = useUser();
  const router = useRouter();

  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [job, setJob] = useState<IngestJob | null>(null);
  const [docs, setDocs] = useState<IngestedDocument[] | null>(null);
  const [docsError, setDocsError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check admin status
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

  const loadDocs = async () => {
    try {
      setDocsError(null);
      const list = await apiGetDocuments();
      setDocs(list);
    } catch (e) {
      setDocsError(e instanceof Error ? e.message : "Failed to load documents");
      setDocs([]);
    }
  };

  useEffect(() => {
    if (isAdmin) loadDocs();
  }, [isAdmin]);

  // Poll job status
  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") return;
    const interval = setInterval(async () => {
      try {
        const updated = await apiGetJobStatus(job.job_id);
        setJob(updated);
        if (updated.status === "done") loadDocs();
      } catch { /* keep polling */ }
    }, 3000);
    return () => clearInterval(interval);
  }, [job]);

  function handleFile(f: File | null | undefined) {
    setError(null);
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setError(tr("admin_wrong_type"));
      return;
    }
    setFile(f);
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);
    setJob(null);
    try {
      const result = await apiUploadDocument(file);
      setJob(result);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

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
        {/* Page title */}
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

        {/* ── Upload card ── */}
        <section className="rounded-2xl border border-border bg-card p-6">
          {/* Drop zone */}
          <label
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              handleFile(e.dataTransfer.files?.[0]);
            }}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition-all ${
              dragging
                ? "border-primary bg-primary/5 scale-[1.01]"
                : file
                ? "border-success bg-success/5"
                : "border-border bg-background hover:border-primary/40 hover:bg-secondary/50"
            }`}
          >
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-xl transition-colors ${
                file ? "bg-success/10 text-success" : "bg-primary/10 text-primary"
              }`}
            >
              <UploadCloud className="h-6 w-6" strokeWidth={1.75} />
            </div>
            <p className="mt-3 text-sm font-medium text-foreground">{tr("admin_drop")}</p>
            {file ? (
              <p className="mt-2 text-xs font-medium text-success">
                {file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            ) : (
              <p className="mt-1 text-xs text-muted-foreground">PDF only</p>
            )}
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf,.pdf"
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </label>

          {error && <div className="mt-4"><ErrorBanner error={error} /></div>}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-semibold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
            style={{ background: "var(--gradient-primary)" }}
          >
            {uploading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Uploading...
              </>
            ) : tr("admin_upload")}
          </button>

          {/* Job status */}
          {job && (
            <div className="mt-4 flex items-center gap-3 rounded-xl border border-border bg-secondary px-4 py-3 text-sm">
              <StatusBadge status={job.status} tr={tr} />
              <span className="font-mono text-xs text-muted-foreground truncate">{job.job_id}</span>
              {job.error && <span className="text-xs text-destructive">{job.error}</span>}
            </div>
          )}
        </section>

        {/* ── Documents table ── */}
        <section className="mt-10">
          <h2 className="text-lg font-semibold text-foreground">{tr("admin_ingested")}</h2>
          <div className="mt-4 overflow-hidden rounded-2xl border border-border bg-card">
            {docs === null ? (
              <div className="flex items-center justify-center p-10">
                <div className="h-7 w-7 animate-spin rounded-full border-2 border-border border-t-primary" />
              </div>
            ) : docsError ? (
              <div className="p-4"><ErrorBanner error={docsError} /></div>
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
      </main>
    </div>
  );
}

function StatusBadge({
  status,
  tr,
}: {
  status: IngestJob["status"];
  tr: (k: "status_queued" | "status_processing" | "status_done" | "status_failed") => string;
}) {
  const map = {
    queued: { label: tr("status_queued"), cls: "bg-secondary text-muted-foreground" },
    processing: { label: tr("status_processing"), cls: "bg-primary/10 text-primary animate-pulse" },
    done: { label: tr("status_done"), cls: "bg-success/10 text-success" },
    failed: { label: tr("status_failed"), cls: "bg-destructive/10 text-destructive" },
  };
  const s = map[status];
  return (
    <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${s.cls}`}>
      {s.label}
    </span>
  );
}
