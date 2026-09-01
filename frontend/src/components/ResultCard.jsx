const LABEL_STYLES = {
  High: { text: "text-signal" },
  Medium: { text: "text-amber-400" },
  Low: { text: "text-muted" },
};

export default function ResultCard({ result }) {
  const { video, viral_potential_score, label } = result;
  const styles = LABEL_STYLES[label] || LABEL_STYLES.Low;

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden animate-[fadeIn_.3s_ease]">
      <div className="grid md:grid-cols-2">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-full h-64 md:h-full object-cover"
        />

        <div className="p-6 md:p-8 flex flex-col justify-between gap-8">
          <div>
            <h2 className="font-display font-semibold text-2xl leading-snug text-ink">{video.title}</h2>
            <p className="font-mono text-xs text-muted mt-2">{video.channel_title}</p>
          </div>

          <div>
            <p className="font-mono text-[10px] tracking-widest text-muted mb-1">GROWTH POTENTIAL</p>
            <p className={`font-display font-bold text-7xl leading-none ${styles.text}`}>
              {viral_potential_score}
              <span className="text-2xl text-muted font-body">/100</span>
            </p>
            <p className={`font-mono text-xs tracking-widest mt-2 ${styles.text}`}>{label.toUpperCase()}</p>
          </div>

          <div className="flex gap-8 font-mono text-xs text-muted border-t border-border pt-6">
            <Stat label="Views" value={video.view_count} />
            <Stat label="Likes" value={video.like_count} />
            <Stat label="Comments" value={video.comment_count} />
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <p className="text-ink text-base">{Intl.NumberFormat("en", { notation: "compact" }).format(value)}</p>
      <p className="text-[10px] tracking-widest mt-1">{label.toUpperCase()}</p>
    </div>
  );
}
