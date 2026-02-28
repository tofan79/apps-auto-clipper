"use client";

interface DownloadManagerProps {
  selectedCount: number;
}

export function DownloadManager({ selectedCount }: DownloadManagerProps): JSX.Element {
  const disabled = selectedCount === 0;
  return (
    <section className="panel">
      <h2 className="panel-title">Download Manager</h2>
      <p className="panel-subtitle">Tahap ini masih baseline UI. Backend download orchestration menyusul.</p>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.7rem" }}>
        <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
          Selected clips: <strong style={{ color: "var(--text)" }}>{selectedCount}</strong>
        </span>
        <button type="button" className="btn btn-primary" disabled={disabled}>
          Download Selected
        </button>
      </div>
    </section>
  );
}
