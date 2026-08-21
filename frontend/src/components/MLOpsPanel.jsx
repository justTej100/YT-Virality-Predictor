import PipelineStrip from "./PipelineStrip.jsx";

export default function MLOpsPanel({ stats }) {
  if (!stats) {
    return (
      <div className="rounded-lg border border-border bg-surface p-5 animate-pulse">
        <div className="h-4 w-32 bg-surface2 rounded mb-4" />
        <div className="h-16 bg-surface2 rounded" />
      </div>
    );
  }

  const isLive = stats.status === "live";

  return (
    <div className="rounded-lg border border-border bg-surface p-5 space-y-5">
      <div className="flex items-center justify-between">
        <p className="font-mono text-xs tracking-widest text-muted">PIPELINE STATUS</p>
        <div className="flex items-center gap-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${isLive ? "bg-signal animate-tally" : "bg-muted"}`} />
          <span className={`font-mono text-[10px] tracking-widest ${isLive ? "text-signal" : "text-muted"}`}>
            {isLive ? "LIVE" : "DEGRADED"}
          </span>
        </div>
      </div>

      <PipelineStrip activeStage="monitor" />

      <dl className="grid grid-cols-2 gap-4">
        <Metric label="Model version" value={`v${stats.model_version}`} />
        <Metric
          label="Validation accuracy"
          value={stats.model_accuracy != null ? `${(stats.model_accuracy * 100).toFixed(1)}%` : "—"}
        />
        <Metric label="Predictions served" value={stats.total_predictions_served} />
        <Metric
          label="Trained"
          value={stats.model_trained_at ? timeAgo(stats.model_trained_at) : "—"}
        />
      </dl>

      {stats.git_commit_sha && (
        <p className="font-mono text-[10px] text-muted/70 pt-1 border-t border-border">
          deploy {stats.git_commit_sha.slice(0, 7)} · {stats.deploy_time ? timeAgo(stats.deploy_time) : "unknown"}
        </p>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <p className="font-mono text-[10px] tracking-widest text-muted mb-1">{label.toUpperCase()}</p>
      <p className="font-display font-semibold text-lg text-ink">{value}</p>
    </div>
  );
}

function timeAgo(isoString) {
  const diffMs = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}
