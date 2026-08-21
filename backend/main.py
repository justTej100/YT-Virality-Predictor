from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
