from fastapi import APIRouter, HTTPException

from app.db.logs import log_prediction
from app.models.predictor import predictor
from app.models.schema import (
    ExplanationItem,
    FeatureBreakdown,
    PredictRequest,
    PredictResponse,
    VideoInfo,
    VoteBreakdown,
)
from app.services.youtube_client import extract_video_id, fetch_video_record
from common.feature_engineering import KNOWN_CATEGORIES

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="No council members are currently loaded. Run ml/train.py to produce one.",
        )

    video_id = extract_video_id(request.video_url)
    video_record = fetch_video_record(video_id)

    result = predictor.predict(video_record)
    features = result["features"]

    log_prediction(
        video_id=video_id,
        title=video_record["title"],
        score=result["score"],
        label=result["label"],
        model_version=predictor.version,
    )

    category_name = KNOWN_CATEGORIES.get(video_record.get("category_id", ""), "other")

    return PredictResponse(
        video=VideoInfo(
            video_id=video_id,
            title=video_record["title"],
            thumbnail_url=video_record["thumbnail_url"],
            channel_title=video_record["channel_title"],
            view_count=video_record["view_count"],
            like_count=video_record["like_count"],
            comment_count=video_record["comment_count"],
        ),
        viral_potential_score=result["score"],
        label=result["label"],
        features=FeatureBreakdown(
            hours_since_upload=round(features["hours_since_upload"], 2),
            views_per_hour=round(features["views_per_hour"], 1),
            like_view_ratio=round(features["like_view_ratio"], 4),
            comment_view_ratio=round(features["comment_view_ratio"], 4),
            subscriber_count=video_record["subscriber_count"],
            category=category_name,
        ),
        council_votes=[VoteBreakdown(**v) for v in result["council_votes"]],
        explanation=[ExplanationItem(**e) for e in result["explanation"]],
        model_version=predictor.version,
    )