from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    video_url: str = Field(..., description="Full YouTube URL or bare video ID")


class FeatureBreakdown(BaseModel):
    hours_since_upload: float
    views_per_hour: float
    like_view_ratio: float
    comment_view_ratio: float
    subscriber_count: int
    category: str


class VideoInfo(BaseModel):
    video_id: str
    title: str
    thumbnail_url: str
    channel_title: str
    view_count: int
    like_count: int
    comment_count: int


class PredictResponse(BaseModel):
    video: VideoInfo
    viral_potential_score: float  # 0-100
    label: str  # "Low" | "Medium" | "High"
    features: FeatureBreakdown
    model_version: int


class StatsResponse(BaseModel):
    model_version: int
    model_trained_at: str | None
    model_accuracy: float | None
    total_predictions_served: int
    deploy_time: str | None
    git_commit_sha: str | None
    status: str
