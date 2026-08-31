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
      <div className="flex items-center gap-3 bg-white rounded-full shadow-sm hover:shadow-md focus-within:shadow-md px-5 py-3.5 transition-shadow">
        <svg
          className="h-5 w-5 text-gray-400 shrink-0"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M8 5v14l11-7z" />
        </svg>
        <input
          id="video-url"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a YouTube link"
          className="flex-1 bg-transparent outline-none text-ink placeholder:text-gray-400 text-base"
        />
      </div>

      <div className="flex justify-center mt-6">
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="bg-white hover:shadow-md disabled:opacity-60 disabled:cursor-not-allowed text-gray-700 text-sm font-medium px-5 py-2.5 rounded-md shadow-sm transition-shadow"
        >
          {loading ? "Analyzing…" : "Predict growth"}
        </button>
      </div>
    </form>
  );
}