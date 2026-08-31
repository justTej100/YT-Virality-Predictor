from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import health, predict, stats
from app.db.database import init_db

app = FastAPI(
    title="YouTube Trend Predictor API",
    description="Predicts short-term viral growth potential for a YouTube video, "
    "backed by an automated train -> deploy -> monitor MLOps pipeline.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's origin before real prod use
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, tags=["prediction"])
app.include_router(health.router, tags=["health"])
app.include_router(stats.router, tags=["stats"])


@app.on_event("startup")
def on_startup():
    init_db()


# Serve the built frontend (if present) so backend + frontend can run as a
# single web service. This is populated by Dockerfile.combined, which builds
# the Vite app and copies frontend/dist into ./static before the image is
# used. Mounted last, and at "/", so it never shadows the API routes above
# (FastAPI matches routes in the order they were registered).
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
