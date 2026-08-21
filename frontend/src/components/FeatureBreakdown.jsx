export default function FeatureBreakdown({ features }) {
  const rows = [
    { label: "Hours since upload", value: features.hours_since_upload.toFixed(1) },
    { label: "Views / hour", value: Intl.NumberFormat("en", { notation: "compact" }).format(features.views_per_hour) },
    { label: "Like : view ratio", value: `${(features.like_view_ratio * 100).toFixed(2)}%` },
    { label: "Comment : view ratio", value: `${(features.comment_view_ratio * 100).toFixed(2)}%` },
    { label: "Channel subscribers", value: Intl.NumberFormat("en", { notation: "compact" }).format(features.subscriber_count) },
    { label: "Category", value: features.category.replace(/_/g, " ") },
  ];

  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <p className="font-mono text-xs tracking-widest text-muted mb-4">WHAT DROVE THIS SCORE</p>
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
        {rows.map((row) => (
          <div key={row.label} className="flex items-baseline justify-between border-b border-border/60 pb-2">
            <dt className="text-sm text-muted">{row.label}</dt>
            <dd className="font-mono text-sm text-data capitalize">{row.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
