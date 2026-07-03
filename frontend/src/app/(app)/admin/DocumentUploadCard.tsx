"use client";

import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { ErrorBanner } from "@/components/ErrorBanner";
import { StatusBadge } from "./StatusBadge";
import { useLanguage } from "@/lib/i18n";
import { useIngestJobPolling } from "@/lib/hooks/useIngestJobPolling";
import { isValidUploadFile } from "@/lib/documents/validateUpload";
import { apiUploadDocument } from "@/lib/api";

type DocumentUploadCardProps = {
  /** Called when a job finishes successfully, so the parent can refresh the documents table. */
  onIngestComplete: () => void;
};

export function DocumentUploadCard({ onIngestComplete }: DocumentUploadCardProps) {
  const { tr } = useLanguage();
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { job, start: startPolling } = useIngestJobPolling(onIngestComplete);

  function handleFile(selected: File | null | undefined) {
    setError(null);
    if (!selected) return;
    if (!isValidUploadFile(selected)) {
      setError(tr("admin_wrong_type"));
      return;
    }
    setFile(selected);
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const result = await apiUploadDocument(file);
      startPolling(result);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="rounded-2xl border border-border bg-card p-6">
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

      {job && (
        <div className="mt-4 flex items-center gap-3 rounded-xl border border-border bg-secondary px-4 py-3 text-sm">
          <StatusBadge status={job.status} tr={tr} />
          <span className="font-mono text-xs text-muted-foreground truncate">{job.job_id}</span>
          {job.error && <span className="text-xs text-destructive">{job.error}</span>}
        </div>
      )}
    </section>
  );
}