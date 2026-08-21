from fastapi import APIRouter

from app.core.config import DEPLOY_TIME, GIT_COMMIT_SHA
from app.db.logs import count_predictions, recent_predictions
from app.models.predictor import predictor
from app.models.schema import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def stats():
    return StatsResponse(
        model_version=predictor.version or 0,
        model_trained_at=predictor.trained_at,
        model_accuracy=predictor.accuracy,
        total_predictions_served=count_predictions(),
        deploy_time=DEPLOY_TIME or None,
        git_commit_sha=GIT_COMMIT_SHA or None,
        status="live" if predictor.is_ready() else "degraded",
    )


@router.get("/stats/recent-predictions")
def stats_recent_predictions():
    return recent_predictions(limit=20)
