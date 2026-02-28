import type {
  ClipItem,
  ClipPreview,
  JobCreatePayload,
  JobItem,
  JobQueueActionResponse,
  JobStatus,
  SettingsResponse
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // ignore json parse failures for non-json responses
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return {} as T;
  }
  return (await response.json()) as T;
}

export const api = {
  listJobs: () => request<JobItem[]>("/jobs"),
  getJobStatus: (jobId: string) => request<JobStatus>(`/jobs/${jobId}/status`),
  createJob: (payload: JobCreatePayload) =>
    request<JobItem>("/jobs", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  cancelJob: (jobId: string) =>
    request<JobQueueActionResponse>(`/jobs/${jobId}/cancel`, { method: "POST" }),
  reorderJob: (jobId: string, index: number) =>
    request<JobQueueActionResponse>(`/jobs/${jobId}/reorder`, {
      method: "POST",
      body: JSON.stringify({ index })
    }),
  listClipsByJob: (jobId: string) => request<ClipItem[]>(`/clips/${jobId}`),
  getClipPreview: (clipId: string) => request<ClipPreview>(`/clips/${clipId}/preview`),
  getSettings: () => request<SettingsResponse>("/settings"),
  updateSettings: (values: Record<string, unknown>) =>
    request<SettingsResponse>("/settings", {
      method: "PUT",
      body: JSON.stringify({ values })
    })
};

export const apiWsUrlForJob = (jobId: string): string => {
  const wsBase = API_BASE.replace(/^http/, "ws");
  return `${wsBase}/ws/${jobId}`;
};
