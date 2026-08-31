// Use `??` (not `||`) so an intentionally empty string is respected. That's
// what the combined single-container build sets, so fetches below resolve
// as same-origin relative paths (e.g. "/predict") instead of falling back
// to localhost. Local `npm run dev` still defaults to localhost:8000 since
// the var is unset (undefined) in that case.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function predictVideo(videoUrl) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_url: videoUrl }),
  });
  return handle(res);
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  return handle(res);
}

export async function fetchRecentPredictions() {
  const res = await fetch(`${API_BASE}/stats/recent-predictions`);
  return handle(res);
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return handle(res);
}
