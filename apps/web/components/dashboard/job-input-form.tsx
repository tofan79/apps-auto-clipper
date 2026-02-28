"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { z } from "zod";

import { api } from "@/lib/api";
import type { JobItem } from "@/lib/types";

const schema = z.object({
  source_url: z.string().min(1, "Source wajib diisi"),
  source_type: z.enum(["youtube", "local"])
});

interface JobInputFormProps {
  onCreated: (job: JobItem) => void;
}

export function JobInputForm({ onCreated }: JobInputFormProps): JSX.Element {
  const queryClient = useQueryClient();
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceType, setSourceType] = useState<"youtube" | "local">("youtube");
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: api.createJob,
    onSuccess: (job) => {
      setSourceUrl("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      onCreated(job);
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : "Gagal membuat job");
    }
  });

  const submit = (): void => {
    const parsed = schema.safeParse({ source_url: sourceUrl, source_type: sourceType });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Input tidak valid");
      return;
    }
    createMutation.mutate(parsed.data);
  };

  return (
    <div>
      <div className="field">
        <label htmlFor="sourceType">Source Type</label>
        <select
          id="sourceType"
          className="select"
          value={sourceType}
          onChange={(event) => setSourceType(event.target.value as "youtube" | "local")}
        >
          <option value="youtube">YouTube URL</option>
          <option value="local">Local File Path</option>
        </select>
      </div>

      <div className="field">
        <label htmlFor="sourceUrl">Video Source</label>
        <textarea
          id="sourceUrl"
          className="textarea"
          rows={3}
          value={sourceUrl}
          onChange={(event) => setSourceUrl(event.target.value)}
          placeholder={sourceType === "youtube" ? "https://www.youtube.com/watch?v=..." : "D:\\Videos\\sample.mp4"}
        />
      </div>

      <div style={{ display: "flex", gap: "0.65rem", alignItems: "center" }}>
        <button
          className="btn btn-primary"
          onClick={submit}
          disabled={createMutation.isPending}
          type="button"
        >
          {createMutation.isPending ? "Membuat..." : "Buat Job"}
        </button>
        {error ? <span style={{ color: "var(--danger)", fontSize: "0.82rem" }}>{error}</span> : null}
      </div>
    </div>
  );
}
