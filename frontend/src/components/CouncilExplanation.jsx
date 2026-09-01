// Shows the two layers of "why this score": how each council member voted
// (model-level disagreement + how much each vote counted), and which
// specific features pushed the combined score up or down (SHAP, weighted
// across the council the same way the score itself is).

function VoteBar({ vote, maxWeight }) {
  const pct = Math.max((vote.weight / maxWeight) * 100, 6);
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="font-mono text-xs text-muted w-8 shrink-0">v{vote.version}</span>
      <div className="flex-1 h-2 rounded-full bg-surface2 overflow-hidden">
        <div className="h-full rounded-full bg-data" style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono text-xs text-ink w-12 text-right shrink-0">{vote.probability}%</span>
      <span className="font-mono text-[10px] text-muted w-16 text-right shrink-0">
        {(vote.weight * 100).toFixed(1)}% wt
      </span>
    </div>
  );
}

function ExplanationBar({ item, maxAbs }) {
  const isUp = item.direction === "up";
  const pct = Math.max((Math.abs(item.contribution) / maxAbs) * 100, 4);
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 text-sm">
      <span className="text-muted truncate">{item.feature.replace(/_/g, " ")}</span>
      <div className="flex items-center gap-2 w-40 justify-end">
        <div className="flex-1 h-2 rounded-full bg-surface2 overflow-hidden">
          <div
            className={`h-full rounded-full ${isUp ? "bg-signal" : "bg-muted"}`}
            style={{ width: `${pct}%`, marginLeft: isUp ? "auto" : 0 }}
          />
        </div>
        <span className={`font-mono text-xs w-6 text-right ${isUp ? "text-signal" : "text-muted"}`}>
          {isUp ? "▲" : "▼"}
        </span>
      </div>
    </div>
  );
}

export default function CouncilExplanation({ councilVotes, explanation }) {
  if (!councilVotes?.length && !explanation?.length) return null;

  const maxWeight = Math.max(...councilVotes.map((v) => v.weight), 0.0001);
  const maxAbs = Math.max(...explanation.map((e) => Math.abs(e.contribution)), 0.0001);

  return (
    <div className="grid sm:grid-cols-2 gap-6">
      <div className="rounded-lg border border-border bg-surface p-5">
        <p className="font-mono text-xs tracking-widest text-muted mb-4">COUNCIL VOTES</p>
        <div className="space-y-2.5">
          {councilVotes.map((vote) => (
            <VoteBar key={vote.version} vote={vote} maxWeight={maxWeight} />
          ))}
        </div>
        <p className="text-[11px] text-muted mt-4">
          Newer models get slightly more say. Final score is the weighted average above.
        </p>
      </div>

      <div className="rounded-lg border border-border bg-surface p-5">
        <p className="font-mono text-xs tracking-widest text-muted mb-4">TOP FACTORS</p>
        <div className="space-y-2.5">
          {explanation.map((item) => (
            <ExplanationBar key={item.feature} item={item} maxAbs={maxAbs} />
          ))}
        </div>
        <p className="text-[11px] text-muted mt-4">
          What pushed this video's score up (▲) or down (▼), combined across the council.
        </p>
      </div>
    </div>
  );
}
