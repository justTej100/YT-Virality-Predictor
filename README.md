# YouTube Trend Predictor — an MLOps Pipeline

Predicts the short-term viral growth potential of a YouTube video (paste a
link, get a score) — but the actual point of this project is the pipeline
around the model: **train → deploy → serve → monitor**, wired together with
real CI/CD.

## Pipeline

```
ml/ (train)  ──►  ml/models/model_vN.pkl + model_metadata.json
                              │
                              ▼
backend/ (serve)  ──►  FastAPI /predict, /stats  ──►  frontend (demo UI)
                              │
                              ▼
                    SQLite prediction_log (monitoring)
```

- **`common/`** — shared feature engineering, imported by both `ml/` and
  `backend/` to prevent train/serve skew.
- **`ml/`** — offline training pipeline. Produces a versioned model artifact
  and a `model_metadata.json` "mini model registry" (version, trained_at,
  accuracy, feature list).
- **`backend/`** — FastAPI service. Loads whatever model is currently marked
  "accepted" in `model_metadata.json` and serves predictions. Logs every
  prediction to SQLite for the monitoring dashboard.
- **`.github/workflows/`** — `ci.yml` runs tests on every push;
  `deploy.yml` re-runs an **accuracy gate** and only deploys to Railway if
  the currently trained model clears the minimum accuracy threshold.

## Quickstart

```bash
# 1. Bootstrap training data (synthetic, so you can train immediately)
python ml/data/generate_synthetic_data.py --n 3000

# 2. Train + version the model
python ml/train.py

# 3. Run the backend
export YOUTUBE_API_KEY=your_key_here   # for live /predict calls
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Try it
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

curl http://localhost:8000/stats
```

## Real data instead of synthetic

`ml/ingestion/poll_trending.py` polls YouTube's trending list + channel stats
and appends snapshots to `ml/data/raw/snapshots.csv`. Run it on a schedule
(cron / GitHub Actions `schedule:` trigger) to accumulate real data, then
build a proper training set from the accumulated snapshots and swap it in for
`ml/train.py`. The synthetic generator exists so the full pipeline is
demoable immediately, not because it's the intended long-term data source.

## Honest scope notes (for the README you show judges)

- Model registry is a JSON file, not MLflow/W&B — intentional for hackathon
  scope; noted as the first upgrade for a real deployment.
- Retraining is manually triggered (`python ml/train.py`) or CI-triggered on
  push, not on a live schedule against fresh data — see "Real data" above for
  how to extend this.
- CORS is wide open (`allow_origins=["*"]`) for demo convenience; would be
  scoped to the frontend's origin in production.

## Docker

Build context must be the **repo root** (not `backend/`), since the image
also needs `common/` and `ml/models/`:

```bash
docker build -f backend/Dockerfile -t yt-trend-predictor .
docker run -p 8000:8000 -e YOUTUBE_API_KEY=your_key yt-trend-predictor
```
