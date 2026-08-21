const STAGES = [
  { key: "data", label: "DATA" },
  { key: "train", label: "TRAIN" },
  { key: "deploy", label: "DEPLOY" },
  { key: "monitor", label: "MONITOR" },
];

/**
 * A broadcast-console "signal chain" — each stage is a tally light, the
 * currently-live stage pulses red like an on-air indicator, and a thin scan
 * line sweeps the chain to suggest live throughput rather than a static
 * numbered list. Grounded in the subject (video / broadcast) rather than a
 * generic step tracker.
 */
export default function PipelineStrip({ activeStage = "monitor" }) {
  const activeIndex = STAGES.findIndex((s) => s.key === activeStage);

  return (
    <div className="relative rounded-lg border border-border bg-surface px-5 py-4 overflow-hidden">
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-30">
        <div className="h-full w-1/3 bg-gradient-to-r from-transparent via-data/40 to-transparent animate-scan" />
      </div>

      <div className="relative flex items-center justify-between gap-1">
        {STAGES.map((stage, i) => {
          const isPast = i < activeIndex;
          const isActive = i === activeIndex;
          return (
            <div key={stage.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center gap-2 shrink-0">
                <span
                  className={[
                    "h-2.5 w-2.5 rounded-full border",
                    isActive
                      ? "bg-signal border-signal animate-tally"
                      : isPast
                      ? "bg-data border-data"
                      : "bg-transparent border-muted/50",
                  ].join(" ")}
                />
                <span
                  className={[
                    "font-mono text-[10px] tracking-widest",
                    isActive ? "text-signal" : isPast ? "text-data" : "text-muted/60",
                  ].join(" ")}
                >
                  {stage.label}
                </span>
              </div>
              {i < STAGES.length - 1 && (
                <div
                  className={[
                    "h-px flex-1 mx-2 mb-4",
                    isPast ? "bg-data/50" : "bg-border",
                  ].join(" ")}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
