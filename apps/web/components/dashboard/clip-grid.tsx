"use client";

import type { ClipItem } from "@/lib/types";

interface ClipGridProps {
  clips: ClipItem[];
  onPreview: (clipId: string) => void;
  selectedClipIds: string[];
  onToggleSelect: (clipId: string) => void;
}

export function ClipGrid({ clips, onPreview, selectedClipIds, onToggleSelect }: ClipGridProps): JSX.Element {
  if (!clips.length) {
    return <p className="panel-subtitle">Belum ada clip untuk job yang dipilih.</p>;
  }
  return (
    <div className="clip-grid">
      {clips.map((clip) => {
        const isSelected = selectedClipIds.includes(clip.id);
        return (
          <article key={clip.id} className="clip-card" onClick={() => onPreview(clip.id)}>
            <div className="clip-thumb">{clip.mode.toUpperCase()}</div>
            <p style={{ margin: "0.55rem 0 0.35rem", fontWeight: 700, fontSize: "0.82rem" }} className="mono">
              {clip.id.slice(0, 10)}
            </p>
            <p style={{ margin: "0", fontSize: "0.78rem", color: "var(--muted)" }}>
              Viral {clip.viral_score} • {clip.duration_sec}s
            </p>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginTop: "0.5rem", padding: "0.35rem 0.55rem", width: "100%" }}
              onClick={(event) => {
                event.stopPropagation();
                onToggleSelect(clip.id);
              }}
            >
              {isSelected ? "Selected" : "Select"}
            </button>
          </article>
        );
      })}
    </div>
  );
}
