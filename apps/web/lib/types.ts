export type JobSourceType = "youtube" | "local";

export interface JobItem {
  id: string;
  user_id: string | null;
  source_url: string;
  source_type: JobSourceType;
  status: string;
  progress_pct: number;
  current_stage: string | null;
  error_msg: string | null;
  checkpoint_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobStatus {
  id: string;
  status: string;
  progress_pct: number;
  current_stage: string | null;
  error_msg: string | null;
}

export interface ClipItem {
  id: string;
  job_id: string;
  file_path: string;
  thumbnail_path: string | null;
  mode: string;
  viral_score: number;
  duration_sec: number;
  created_at: string;
}

export interface ClipPreview {
  clip_id: string;
  file_path: string;
  thumbnail_path: string | null;
  metadata: Record<string, unknown>;
}

export interface JobCreatePayload {
  source_url: string;
  source_type: JobSourceType;
  user_id?: string;
}

export interface JobQueueActionResponse {
  id: string;
  accepted: boolean;
}

export interface ProgressEvent {
  job_id: string;
  status: string;
  progress_pct: number;
  current_stage: string | null;
  message?: string | null;
  timestamp: string;
}

export interface SettingsResponse {
  values: Record<string, unknown>;
}
