const LABEL_STYLES = {
  High: { text: "text-signal", ring: "ring-signal/40", bar: "bg-signal" },
  Medium: { text: "text-amber-400", ring: "ring-amber-400/40", bar: "bg-amber-400" },
  Low: { text: "text-muted", ring: "ring-muted/30", bar: "bg-muted" },
};

export default function ResultCard({ result }) {
  const { video, viral_potential_score, label } = result;
  const styles = LABEL_STYLES[label] || LABEL_STYLES.Low;

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden animate-[fadeIn_.3s_ease]">
      <div className="flex flex-col md:flex-row">
        <div className="md:w-64 shrink-0 relative">
          <img
            src={video.thumbnail_url}
            alt={video.title}
            className="w-full h-40 md:h-full object-cover"
          />
          <div
            className={`absolute top-2 left-2 flex items-center gap-1.5 rounded-full bg-base/80 backdrop-blur px-2.5 py-1 ring-1 ${styles.ring}`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${styles.bar}`} />
            <span className={`font-mono text-[10px] tracking-widest ${styles.text}`}>{label.toUpperCase()}</span>
          </div>
        </div>

        <div className="flex-1 p-5 flex flex-col justify-between gap-4">
          <div>
            <h2 className="font-display font-semibold text-lg leading-snug text-ink">{video.title}</h2>
            <p className="font-mono text-xs text-muted mt-1">{video.channel_title}</p>
          </div>

          <div className="flex items-end justify-between gap-6">
            <div>
              <p className="font-mono text-[10px] tracking-widest text-muted mb-1">GROWTH POTENTIAL</p>
              <p className={`font-display font-bold text-4xl ${styles.text}`}>
                {viral_potential_score}
                <span className="text-lg text-muted font-body">/100</span>
              </p>
            </div>
            <div className="flex gap-5 font-mono text-xs text-muted">
              <Stat label="Views" value={video.view_count} />
              <Stat label="Likes" value={video.like_count} />
              <Stat label="Comments" value={video.comment_count} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="text-right">
      <p className="text-ink text-sm">{Intl.NumberFormat("en", { notation: "compact" }).format(value)}</p>
      <p className="text-[10px] tracking-widest">{label.toUpperCase()}</p>
    </div>
  );
}
