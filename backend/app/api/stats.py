from fastapi import APIRouter

from app.core.config import DEPLOY_TIME, GIT_COMMIT_SHA
from app.db.logs import count_predictions, recent_predictions
from app.models.predictor import predictor
from app.models.schema import CouncilMember, StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def stats():
    return StatsResponse(
        council=[
            CouncilMember(
                version=m["version"],
                accuracy=m["accuracy"],
                weight=round(m["weight"], 3),
                trained_at=m["trained_at"],
            )
            for m in predictor.council
        ],
        total_predictions_served=count_predictions(),
        deploy_time=DEPLOY_TIME or None,
        git_commit_sha=GIT_COMMIT_SHA or None,
        status="live" if predictor.is_ready() else "degraded",
    )


@router.get("/stats/recent-predictions")
def stats_recent_predictions():
    return recent_predictions(limit=20)