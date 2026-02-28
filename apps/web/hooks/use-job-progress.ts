"use client";

import { useEffect } from "react";

import { apiWsUrlForJob } from "@/lib/api";
import type { ProgressEvent } from "@/lib/types";
import { useQueueStore } from "@/stores/use-queue-store";

export function useJobProgress(jobId: string | null): void {
  const upsertProgress = useQueueStore((state) => state.upsertProgress);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    const ws = new WebSocket(apiWsUrlForJob(jobId));
    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as ProgressEvent;
        if (parsed.job_id) {
          upsertProgress(parsed);
        }
      } catch {
        // Ignore malformed messages.
      }
    };

    const ping = window.setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 20_000);

    return () => {
      window.clearInterval(ping);
      ws.close();
    };
  }, [jobId, upsertProgress]);
}
