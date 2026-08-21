"""
Shared feature engineering.

CRITICAL: this module is imported by BOTH the training pipeline (ml/train.py)
and the live serving API (backend/app/services). Using the exact same code in
both places prevents "train/serve skew" - a classic real-world MLOps bug where
the features used to train a model don't quite match the features computed at
inference time, silently degrading model performance in production.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

# Feature order matters: the model is trained on a fixed-order vector, so any
# change here must be matched by retraining. FEATURE_NAMES is the single
# source of truth for that order.
FEATURE_NAMES = [
    "hours_since_upload",
    "views_per_hour",
    "like_view_ratio",
    "comment_view_ratio",
    "title_length",
    "title_word_count",
    "has_number_in_title",
    "has_bracket_in_title",
    "tag_count",
    "duration_seconds",
    "is_short_form",  # < 60s
    "subscriber_count_log",
    "channel_video_count_log",
    "views_to_subscriber_ratio",
]

CATEGORY_FEATURE_PREFIX = "category_"

# A small fixed set of common YouTube category IDs -> names, used for one-hot
# encoding. Anything outside this set falls back to "other".
KNOWN_CATEGORIES = {
    "1": "film_animation",
    "2": "autos_vehicles",
    "10": "music",
    "15": "pets_animals",
    "17": "sports",
    "19": "travel_events",
    "20": "gaming",
    "22": "people_blogs",
    "23": "comedy",
    "24": "entertainment",
    "25": "news_politics",
    "26": "howto_style",
    "27": "education",
    "28": "science_technology",
}


def _parse_iso8601_duration_to_seconds(duration: str) -> int:
    """Parse YouTube's ISO 8601 duration format, e.g. 'PT4M13S' -> 253."""
    if not duration:
        return 0
    match = re.match(
        r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?",
        duration,
    )
    if not match:
        return 0
    parts = match.groupdict()
    hours = int(parts["hours"] or 0)
    minutes = int(parts["minutes"] or 0)
    seconds = int(parts["seconds"] or 0)
    return hours * 3600 + minutes * 60 + seconds


def _safe_log(value: float) -> float:
    import math

    return math.log1p(max(value, 0))


def build_feature_vector(video: dict[str, Any]) -> dict[str, float]:
    """
    Build a feature dict from a normalized video record.

    Expected `video` shape (this is the normalized internal schema - both the
    training data builder and the live YouTube client produce records in this
    shape before calling this function):

    {
        "published_at": "2026-08-15T12:00:00Z",
        "fetched_at": "2026-08-16T09:00:00Z",   # when stats were pulled
        "view_count": 125000,
        "like_count": 8400,
        "comment_count": 620,
        "title": "I Tried This For 30 Days...",
        "tags": ["challenge", "vlog"],
        "category_id": "24",
        "duration": "PT10M32S",
        "subscriber_count": 450000,
        "channel_video_count": 812,
    }
    """
    published_at = _parse_dt(video["published_at"])
    fetched_at = _parse_dt(video.get("fetched_at") or datetime.now(timezone.utc).isoformat())

    hours_since_upload = max((fetched_at - published_at).total_seconds() / 3600.0, 1 / 60)

    view_count = float(video.get("view_count") or 0)
    like_count = float(video.get("like_count") or 0)
    comment_count = float(video.get("comment_count") or 0)
    subscriber_count = float(video.get("subscriber_count") or 0)
    channel_video_count = float(video.get("channel_video_count") or 0)

    title = video.get("title") or ""
    tags = video.get("tags") or []
    duration_seconds = _parse_iso8601_duration_to_seconds(video.get("duration") or "")

    features: dict[str, float] = {
        "hours_since_upload": hours_since_upload,
        "views_per_hour": view_count / hours_since_upload,
        "like_view_ratio": like_count / view_count if view_count else 0.0,
        "comment_view_ratio": comment_count / view_count if view_count else 0.0,
        "title_length": float(len(title)),
        "title_word_count": float(len(title.split())),
        "has_number_in_title": float(bool(re.search(r"\d", title))),
        "has_bracket_in_title": float(bool(re.search(r"[\[\](){}]", title))),
        "tag_count": float(len(tags)),
        "duration_seconds": float(duration_seconds),
        "is_short_form": float(duration_seconds > 0 and duration_seconds < 60),
        "subscriber_count_log": _safe_log(subscriber_count),
        "channel_video_count_log": _safe_log(channel_video_count),
        "views_to_subscriber_ratio": view_count / subscriber_count if subscriber_count else 0.0,
    }

    # One-hot encode category
    category_id = str(video.get("category_id") or "")
    category_name = KNOWN_CATEGORIES.get(category_id, "other")
    for name in list(KNOWN_CATEGORIES.values()) + ["other"]:
        features[f"{CATEGORY_FEATURE_PREFIX}{name}"] = float(category_name == name)

    return features


def feature_dict_to_vector(features: dict[str, float]) -> list[float]:
    """Flatten a feature dict into an ordered list matching model input order."""
    ordered_names = full_feature_name_list()
    return [features.get(name, 0.0) for name in ordered_names]


def full_feature_name_list() -> list[str]:
    category_names = [f"{CATEGORY_FEATURE_PREFIX}{name}" for name in list(KNOWN_CATEGORIES.values()) + ["other"]]
    return FEATURE_NAMES + category_names


def _parse_dt(value: str) -> datetime:
    # Handles both 'Z' suffix and '+00:00' style ISO timestamps
    value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)
