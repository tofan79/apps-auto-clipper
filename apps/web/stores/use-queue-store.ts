"use client";

import { create } from "zustand";

import type { ProgressEvent } from "@/lib/types";

interface QueueState {
  progressByJob: Record<string, ProgressEvent>;
  upsertProgress: (event: ProgressEvent) => void;
  clearProgress: (jobId: string) => void;
}

export const useQueueStore = create<QueueState>((set) => ({
  progressByJob: {},
  upsertProgress: (event) =>
    set((state) => ({
      progressByJob: {
        ...state.progressByJob,
        [event.job_id]: event
      }
    })),
  clearProgress: (jobId) =>
    set((state) => {
      const next = { ...state.progressByJob };
      delete next[jobId];
      return { progressByJob: next };
    })
}));
