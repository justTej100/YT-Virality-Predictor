"""
Basic smoke test for the prediction pipeline using a synthetic video record,
bypassing the live YouTube API call (no network/API key needed in CI).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.models.predictor import predictor  # noqa: E402


def _sample_video_record():
    from datetime import datetime, timedelta, timezone

    return {
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "view_count": 50000,
        "like_count": 3200,
        "comment_count": 410,
        "title": "I Tried AI For 30 Days",
        "tags": ["ai", "challenge", "tech"],
        "category_id": "28",
        "duration": "PT8M12S",
        "subscriber_count": 250000,
        "channel_video_count": 340,
    }


def test_model_is_loaded():
    assert predictor.is_ready(), "No accepted model found - run ml/train.py first."


def test_predict_returns_valid_output():
    result = predictor.predict(_sample_video_record())
    assert 0 <= result["score"] <= 100
    assert result["label"] in {"Low", "Medium", "High"}
