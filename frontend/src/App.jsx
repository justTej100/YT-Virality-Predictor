import { useEffect, useState } from "react";
import { predictVideo, fetchStats, fetchRecentPredictions } from "./api/client.js";
import PredictForm from "./components/PredictForm.jsx";
import ResultCard from "./components/ResultCard.jsx";
import FeatureBreakdown from "./components/FeatureBreakdown.jsx";
import MLOpsPanel from "./components/MLOpsPanel.jsx";
import PredictionLog from "./components/PredictionLog.jsx";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [predictions, setPredictions] = useState([]);

  async function loadSidebar() {
    try {
      const [statsData, predsData] = await Promise.all([fetchStats(), fetchRecentPredictions()]);
      setStats(statsData);
      setPredictions(predsData);
    } catch {
      // Sidebar is supplementary — a failed refresh here shouldn't block the
      // main predict flow, so we swallow it silently rather than surfacing
      // an error banner for a non-critical panel.
    }
  }

  useEffect(() => {
    loadSidebar();
  }, []);

  async function handlePredict(videoUrl) {
    setLoading(true);
    setError(null);
    try {
      const data = await predictVideo(videoUrl);
      setResult(data);
      loadSidebar();
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen max-w-6xl mx-auto px-6 py-10">
      <header className="flex items-center justify-between mb-10">
        <div>
          <p className="font-mono text-xs tracking-widest text-data mb-1">TRENDCAST</p>
          <h1 className="font-display font-bold text-2xl text-ink">Viral Growth Predictor</h1>
        </div>
        <div className="hidden sm:flex items-center gap-2 font-mono text-[10px] tracking-widest text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-signal animate-tally" />
          MLOPS PIPELINE
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        <main className="space-y-6">
          <div className="rounded-lg border border-border bg-surface p-6">
            <PredictForm onSubmit={handlePredict} loading={loading} />
            {error && (
              <p className="mt-3 font-mono text-xs text-signal">{error}</p>
            )}
          </div>

          {loading && <SkeletonResult />}

          {!loading && result && (
            <>
              <ResultCard result={result} />
              <FeatureBreakdown features={result.features} />
            </>
          )}

          {!loading && !result && (
            <div className="rounded-lg border border-dashed border-border p-10 text-center">
              <p className="text-muted text-sm">
                Paste a YouTube link above to see its predicted growth potential.
              </p>
            </div>
          )}
        </main>

        <aside className="space-y-6">
          <MLOpsPanel stats={stats} />
          <PredictionLog predictions={predictions} />
        </aside>
      </div>

      <footer className="mt-16 pt-6 border-t border-border font-mono text-[10px] text-muted/60 text-center">
        Trained model → deployed API → live monitoring. Every prediction above is logged and served by the pipeline shown in the sidebar.
      </footer>
    </div>
  );
}

function SkeletonResult() {
  return (
    <div className="rounded-lg border border-border bg-surface p-6 animate-pulse">
      <div className="h-40 bg-surface2 rounded-md mb-4" />
      <div className="h-4 w-2/3 bg-surface2 rounded mb-2" />
      <div className="h-4 w-1/3 bg-surface2 rounded" />
    </div>
  );
}
