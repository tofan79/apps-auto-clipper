"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { ClipGrid } from "@/components/dashboard/clip-grid";
import { ClipPreviewModal } from "@/components/dashboard/clip-preview-modal";
import { DownloadManager } from "@/components/dashboard/download-manager";
import { JobInputForm } from "@/components/dashboard/job-input-form";
import { QueuePanel } from "@/components/dashboard/queue-panel";
import { Card } from "@/components/ui/card";
import { useJobProgress } from "@/hooks/use-job-progress";
import { api } from "@/lib/api";
import { useJobStore } from "@/stores/use-job-store";
import { useQueueStore } from "@/stores/use-queue-store";

export default function DashboardPage(): JSX.Element {
  const selectedJobId = useJobStore((state) => state.selectedJobId);
  const setSelectedJobId = useJobStore((state) => state.setSelectedJobId);
  const progressByJob = useQueueStore((state) => state.progressByJob);

  const [selectedClipIds, setSelectedClipIds] = useState<string[]>([]);
  const [previewClipId, setPreviewClipId] = useState<string | null>(null);

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: api.listJobs,
    refetchInterval: 2500
  });

  useEffect(() => {
    if (!selectedJobId && jobsQuery.data && jobsQuery.data.length > 0) {
      setSelectedJobId(jobsQuery.data[0].id);
    }
  }, [jobsQuery.data, selectedJobId, setSelectedJobId]);

  useJobProgress(selectedJobId);

  const clipsQuery = useQuery({
    queryKey: ["clips", selectedJobId],
    queryFn: () => api.listClipsByJob(selectedJobId as string),
    enabled: Boolean(selectedJobId),
    refetchInterval: 3500
  });

  const previewQuery = useQuery({
    queryKey: ["clip-preview", previewClipId],
    queryFn: () => api.getClipPreview(previewClipId as string),
    enabled: Boolean(previewClipId)
  });

  const activeJobs = useMemo(() => jobsQuery.data ?? [], [jobsQuery.data]);
  const activeClips = clipsQuery.data ?? [];
  const selectedJob = useMemo(
    () => activeJobs.find((item) => item.id === selectedJobId) ?? null,
    [activeJobs, selectedJobId]
  );

  return (
    <>
      <section className="grid-main">
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
          <Card title="Create Job" subtitle="YouTube URL atau local file path.">
            <JobInputForm
              onCreated={(job) => {
                setSelectedJobId(job.id);
              }}
            />
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
          <Card
            title="Job Focus"
            subtitle={
              selectedJob
                ? `Status ${selectedJob.status} | ${progressByJob[selectedJob.id]?.progress_pct ?? selectedJob.progress_pct}%`
                : "Pilih job dari panel queue"
            }
          >
            <div className="mono" style={{ fontSize: "0.76rem", opacity: 0.9 }}>
              {selectedJob?.id ?? "No job selected"}
            </div>
            <p className="panel-subtitle" style={{ marginTop: "0.65rem" }}>
              Stage: {progressByJob[selectedJob?.id ?? ""]?.current_stage ?? selectedJob?.current_stage ?? "-"}
            </p>
          </Card>
        </motion.div>
      </section>

      <section className="grid-main">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.23 }}>
          <Card title="Queue" subtitle="Realtime progress via polling + websocket.">
            <QueuePanel
              jobs={activeJobs}
              selectedJobId={selectedJobId}
              progressByJob={progressByJob}
              onSelectJob={(jobId) => {
                setSelectedJobId(jobId);
                setSelectedClipIds([]);
              }}
            />
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.28 }}>
          <Card title="Clips" subtitle={selectedJobId ? `Loaded for ${selectedJobId.slice(0, 12)}` : "Select job first"}>
            <ClipGrid
              clips={activeClips}
              onPreview={setPreviewClipId}
              selectedClipIds={selectedClipIds}
              onToggleSelect={(clipId) => {
                setSelectedClipIds((current) =>
                  current.includes(clipId) ? current.filter((item) => item !== clipId) : [...current, clipId]
                );
              }}
            />
          </Card>
        </motion.div>
      </section>

      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <DownloadManager selectedCount={selectedClipIds.length} />
      </motion.div>

      <ClipPreviewModal preview={previewQuery.data ?? null} onClose={() => setPreviewClipId(null)} />
    </>
  );
}
