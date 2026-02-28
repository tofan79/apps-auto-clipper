interface StatusPillProps {
  status: string;
}

export function StatusPill({ status }: StatusPillProps): JSX.Element {
  const normalized = status.toLowerCase();
  const className =
    normalized === "running"
      ? "status-pill status-running"
      : normalized === "done"
        ? "status-pill status-done"
        : normalized === "failed" || normalized === "canceled"
          ? "status-pill status-failed"
          : "status-pill";
  return <span className={className}>{status}</span>;
}
