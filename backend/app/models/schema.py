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


class VoteBreakdown(BaseModel):
    version: int
    probability: float  # this council member's own 0-100 score
    weight: float  # this member's share of the final weighted vote


class ExplanationItem(BaseModel):
    feature: str
    contribution: float  # signed, log-odds scale, weighted across the council
    direction: str  # "up" | "down"


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
    viral_potential_score: float  # 0-100, weighted across the council
    label: str  # "Low" | "Medium" | "High"
    features: FeatureBreakdown
    council_votes: list[VoteBreakdown]
    explanation: list[ExplanationItem]
    model_version: int  # newest (highest-weighted) council member, for logging


class CouncilMember(BaseModel):
    version: int
    accuracy: float
    weight: float
    trained_at: str | None


class StatsResponse(BaseModel):
    council: list[CouncilMember]
    total_predictions_served: int
    deploy_time: str | None
    git_commit_sha: str | None
    status: str