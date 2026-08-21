import { useState } from "react";

export default function PredictForm({ onSubmit, loading }) {
  const [url, setUrl] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim() || loading) return;
    onSubmit(url.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <label htmlFor="video-url" className="block font-mono text-xs tracking-widest text-muted mb-2">
        PASTE A YOUTUBE LINK
      </label>
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          id="video-url"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          className="flex-1 bg-surface border border-border rounded-md px-4 py-3 text-ink placeholder:text-muted/60 font-mono text-sm focus:border-data transition-colors"
        />
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="shrink-0 bg-signal hover:bg-signal/90 disabled:bg-surface2 disabled:text-muted disabled:cursor-not-allowed text-white font-display font-semibold px-6 py-3 rounded-md transition-colors"
        >
          {loading ? "Analyzing…" : "Predict"}
        </button>
      </div>
    </form>
  );
}
