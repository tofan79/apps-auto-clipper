"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { JobItem, ProgressEvent } from "@/lib/types";
import { StatusPill } from "@/components/ui/status-pill";

interface QueuePanelProps {
  jobs: JobItem[];
  selectedJobId: string | null;
  progressByJob: Record<string, ProgressEvent>;
  onSelectJob: (jobId: string) => void;
}

export function QueuePanel({
  jobs,
  selectedJobId,
  progressByJob,
  onSelectJob
}: QueuePanelProps): JSX.Element {
  const queryClient = useQueryClient();
  const cancelMutation = useMutation({
    mutationFn: api.cancelJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  });

  if (!jobs.length) {
    return <p className="panel-subtitle">Belum ada job. Mulai dari panel Input.</p>;
  }

  return (
    <div className="list">
      {jobs.map((job) => {
        const progress = progressByJob[job.id]?.progress_pct ?? job.progress_pct;
        const stage = progressByJob[job.id]?.current_stage ?? job.current_stage ?? "queued";
        const isSelected = selectedJobId === job.id;
        return (
          <div
            key={job.id}
            className="job-card"
            style={isSelected ? { borderColor: "rgba(64, 217, 177, 0.85)" } : undefined}
          >
            <div className="job-top">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => onSelectJob(job.id)}
                style={{ padding: "0.35rem 0.6rem" }}
              >
                Select
              </button>
              <StatusPill status={job.status} />
            </div>

            <p className="mono" style={{ margin: "0.6rem 0 0.2rem", fontSize: "0.74rem", opacity: 0.9 }}>
              {job.id}
            </p>
            <p style={{ margin: "0", fontSize: "0.8rem", color: "var(--muted)" }}>
              Stage: {stage} • {progress}%
            </p>
            <div className="progress-rail">
              <div className="progress-fill" style={{ width: `${Math.max(0, Math.min(100, progress))}%` }} />
            </div>

            <div style={{ marginTop: "0.6rem", display: "flex", gap: "0.5rem" }}>
              <button
                className="btn btn-danger"
                onClick={() => cancelMutation.mutate(job.id)}
                type="button"
                disabled={cancelMutation.isPending || job.status === "done" || job.status === "failed"}
              >
                Cancel
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
