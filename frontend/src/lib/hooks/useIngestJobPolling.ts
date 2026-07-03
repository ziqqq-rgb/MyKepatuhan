"use client";

import { useEffect, useState } from "react";
import { apiGetJobStatus, type IngestJob } from "@/lib/api";

const POLL_INTERVAL_MS = 3000;

/**
 * Polls an ingest job's status every 3s until it settles into done/failed.
 * Call `start(job)` after upload succeeds; polling stops automatically
 * once the job finishes or a new job is started.
 */
export function useIngestJobPolling(onDone: () => void) {
  const [job, setJob] = useState<IngestJob | null>(null);

  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") return;

    const interval = setInterval(async () => {
      try {
        const updated = await apiGetJobStatus(job.job_id);
        setJob(updated);
        if (updated.status === "done") onDone();
      } catch {
        // A transient network error shouldn't abandon the job — keep polling.
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [job, onDone]);

  return { job, start: setJob };
}