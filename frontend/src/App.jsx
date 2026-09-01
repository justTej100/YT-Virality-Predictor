import { useState } from "react";
import { predictVideo } from "./api/client.js";
import PredictForm from "./components/PredictForm.jsx";
import ResultCard from "./components/ResultCard.jsx";
import FeatureBreakdown from "./components/FeatureBreakdown.jsx";
import CouncilExplanation from "./components/CouncilExplanation.jsx";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handlePredict(videoUrl) {
    setLoading(true);
    setError(null);
    try {
      const data = await predictVideo(videoUrl);
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  // Mirrors google.com's own shift: centered on first load, top-aligned once
  // there's something to show, so results have room to breathe below.
  const hasContent = loading || result || error;

  return (
    <div
      className={`min-h-screen flex flex-col items-center px-6 pb-16 transition-all ${
        hasContent ? "justify-start pt-14 sm:pt-20" : "justify-center"
      }`}
    >
      <div className="w-full max-w-xl">
        <h1 className="text-center font-display font-bold text-5xl sm:text-6xl text-white mb-8 tracking-tight">
          YT Virality Predictor
        </h1>

        <PredictForm onSubmit={handlePredict} loading={loading} />

        {error && (
          <p className="mt-4 text-center text-sm text-white">{error}</p>
        )}
      </div>

      {loading && (
        <div className="w-full max-w-5xl mt-8">
          <SkeletonResult />
        </div>
      )}

      {!loading && result && (
        <div className="w-full max-w-5xl mt-8 space-y-6">
          <ResultCard result={result} />
          <FeatureBreakdown features={result.features} />
          <CouncilExplanation councilVotes={result.council_votes} explanation={result.explanation} />
        </div>
      )}
    </div>
  );
}

function SkeletonResult() {
  return (
    <div className="rounded-lg bg-white p-6 animate-pulse">
      <div className="grid md:grid-cols-2 gap-6">
        <div className="h-72 bg-surface2 rounded-md" />
        <div className="flex flex-col gap-3 py-2">
          <div className="h-6 w-3/4 bg-surface2 rounded" />
          <div className="h-4 w-1/3 bg-surface2 rounded" />
          <div className="h-16 w-1/2 bg-surface2 rounded mt-6" />
        </div>
      </div>
    </div>
  );
}