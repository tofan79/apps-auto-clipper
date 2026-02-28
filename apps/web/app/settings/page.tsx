"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useSettingsStore } from "@/stores/use-settings-store";

export default function SettingsPage(): JSX.Element {
  const settings = useSettingsStore((state) => state.values);
  const setValues = useSettingsStore((state) => state.setValues);
  const patchValue = useSettingsStore((state) => state.patchValue);
  const [notice, setNotice] = useState<string>("");

  const settingsQuery = useQuery({
    queryKey: ["settings"],
    queryFn: api.getSettings
  });

  useEffect(() => {
    if (settingsQuery.data?.values) {
      setValues(settingsQuery.data.values);
    }
  }, [settingsQuery.data, setValues]);

  const updateMutation = useMutation({
    mutationFn: api.updateSettings,
    onSuccess: (payload) => {
      setValues(payload.values);
      setNotice("Settings updated");
    },
    onError: (err) => {
      setNotice(err instanceof Error ? err.message : "Update failed");
    }
  });

  return (
    <div className="settings-wrap">
      <Card title="Settings" subtitle="Konfigurasi runtime frontend untuk backend lokal.">
        <div className="field">
          <label htmlFor="provider">LLM Provider</label>
          <select
            id="provider"
            className="select"
            value={String(settings.LLM_PROVIDER ?? "openrouter")}
            onChange={(event) => patchValue("LLM_PROVIDER", event.target.value)}
          >
            <option value="openrouter">openrouter</option>
            <option value="ollama">ollama</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="maxclips">Max Clips</label>
          <input
            id="maxclips"
            className="input"
            type="number"
            min={1}
            max={20}
            value={Number(settings.MAX_CLIPS ?? 10)}
            onChange={(event) => patchValue("MAX_CLIPS", Number(event.target.value))}
          />
        </div>

        <div className="field">
          <label htmlFor="preset">FFmpeg Preset</label>
          <select
            id="preset"
            className="select"
            value={String(settings.FFMPEG_PRESET ?? "veryfast")}
            onChange={(event) => patchValue("FFMPEG_PRESET", event.target.value)}
          >
            <option value="ultrafast">ultrafast</option>
            <option value="veryfast">veryfast</option>
            <option value="faster">faster</option>
          </select>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={() => updateMutation.mutate(settings)}
          disabled={updateMutation.isPending}
        >
          {updateMutation.isPending ? "Saving..." : "Save Settings"}
        </button>
        {notice ? <p className="panel-subtitle" style={{ marginTop: "0.7rem" }}>{notice}</p> : null}
      </Card>
    </div>
  );
}
