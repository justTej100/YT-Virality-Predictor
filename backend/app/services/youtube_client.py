import re
from datetime import datetime, timezone

from fastapi import HTTPException
from googleapiclient.discovery import build

from app.core.config import YOUTUBE_API_KEY

_VIDEO_ID_PATTERNS = [
    r"(?:v=|\/videos\/|embed\/|youtu\.be\/|\/shorts\/)([A-Za-z0-9_-]{11})",
]


def extract_video_id(video_url_or_id: str) -> str:
    candidate = video_url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        return candidate
    for pattern in _VIDEO_ID_PATTERNS:
        match = re.search(pattern, candidate)
        if match:
            return match.group(1)
    raise HTTPException(status_code=400, detail="Could not parse a YouTube video ID from that input.")


def _client():
    if not YOUTUBE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="YOUTUBE_API_KEY is not configured on the server.",
        )
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def fetch_video_record(video_id: str) -> dict:
    """Fetch a single video + its channel stats, normalized to the internal
    schema expected by common.feature_engineering.build_feature_vector."""
    youtube = _client()

    video_resp = (
        youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id).execute()
    )
    items = video_resp.get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Video not found (private, deleted, or invalid ID).")

    item = items[0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    channel_id = snippet.get("channelId", "")

    channel_resp = youtube.channels().list(part="statistics", id=channel_id).execute()
    channel_items = channel_resp.get("items", [])
    channel_stats = channel_items[0]["statistics"] if channel_items else {}

    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "tags": snippet.get("tags", []),
        "category_id": snippet.get("categoryId", ""),
        "duration": content.get("duration", ""),
        "subscriber_count": int(channel_stats.get("subscriberCount", 0)),
        "channel_video_count": int(channel_stats.get("videoCount", 0)),
    }
