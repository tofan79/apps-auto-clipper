"use client";

import { create } from "zustand";

interface JobState {
  selectedJobId: string | null;
  selectedClipId: string | null;
  setSelectedJobId: (jobId: string | null) => void;
  setSelectedClipId: (clipId: string | null) => void;
}

export const useJobStore = create<JobState>((set) => ({
  selectedJobId: null,
  selectedClipId: null,
  setSelectedJobId: (selectedJobId) => set({ selectedJobId }),
  setSelectedClipId: (selectedClipId) => set({ selectedClipId })
}));
