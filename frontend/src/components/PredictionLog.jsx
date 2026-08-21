const LABEL_COLOR = {
  High: "text-signal",
  Medium: "text-amber-400",
  Low: "text-muted",
};

export default function PredictionLog({ predictions }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <p className="font-mono text-xs tracking-widest text-muted mb-4">RECENT PREDICTIONS</p>

      {predictions.length === 0 ? (
        <p className="text-sm text-muted/70 py-6 text-center">
          No predictions logged yet — run one above to see it here.
        </p>
      ) : (
        <div className="space-y-1">
          {predictions.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between gap-3 py-2 border-b border-border/50 last:border-0"
            >
              <span className="text-sm text-ink truncate flex-1">{p.title}</span>
              <span className={`font-mono text-xs shrink-0 ${LABEL_COLOR[p.label] || "text-muted"}`}>
                {p.viral_potential_score}
              </span>
              <span className="font-mono text-[10px] text-muted/60 shrink-0 w-16 text-right">
                v{p.model_version}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
