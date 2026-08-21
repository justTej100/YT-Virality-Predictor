"""
Polls YouTube's trending list + tracked videos and appends stat snapshots to
a local CSV. Run this on a schedule (cron, GitHub Actions schedule, etc.) to
accumulate real training data over time.

Usage:
    export YOUTUBE_API_KEY=your_key_here
    python ml/ingestion/poll_trending.py --region US --category 0

Each run appends one row per video to ml/data/raw/snapshots.csv with the
UTC timestamp of the poll. Running this every 15-30 min lets you later
compute view/like/comment VELOCITY between consecutive snapshots of the
same video_id, which is the strongest predictive signal for the model.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from googleapiclient.discovery import build

RAW_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "snapshots.csv"

CSV_COLUMNS = [
    "fetched_at",
    "video_id",
    "title",
    "channel_id",
    "category_id",
    "published_at",
    "duration",
    "tags",
    "view_count",
    "like_count",
    "comment_count",
    "subscriber_count",
    "channel_video_count",
]


def get_youtube_client():
    api_key = os.environ["YOUTUBE_API_KEY"]
    return build("youtube", "v3", developerKey=api_key)


def fetch_trending(youtube, region: str, category: str, max_results: int = 50) -> list[dict]:
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode=region,
        videoCategoryId=category or None,
        maxResults=max_results,
    )
    response = request.execute()
    return response.get("items", [])


def fetch_channel_stats(youtube, channel_ids: list[str]) -> dict[str, dict]:
    """Batch-fetch channel stats (max 50 ids per call, per API limits)."""
    stats_by_channel: dict[str, dict] = {}
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i : i + 50]
        response = youtube.channels().list(part="statistics", id=",".join(batch)).execute()
        for item in response.get("items", []):
            stats_by_channel[item["id"]] = item["statistics"]
    return stats_by_channel


def rows_from_api_response(videos: list[dict], channel_stats: dict[str, dict], fetched_at: str) -> list[dict]:
    rows = []
    for v in videos:
        snippet = v.get("snippet", {})
        stats = v.get("statistics", {})
        content = v.get("contentDetails", {})
        channel_id = snippet.get("channelId", "")
        ch_stats = channel_stats.get(channel_id, {})

        rows.append(
            {
                "fetched_at": fetched_at,
                "video_id": v.get("id", ""),
                "title": snippet.get("title", "").replace("\n", " "),
                "channel_id": channel_id,
                "category_id": snippet.get("categoryId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "duration": content.get("duration", ""),
                "tags": "|".join(snippet.get("tags", [])),
                "view_count": stats.get("viewCount", 0),
                "like_count": stats.get("likeCount", 0),
                "comment_count": stats.get("commentCount", 0),
                "subscriber_count": ch_stats.get("subscriberCount", 0),
                "channel_video_count": ch_stats.get("videoCount", 0),
            }
        )
    return rows


def append_rows(rows: list[dict]) -> None:
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = RAW_DATA_PATH.exists()
    with open(RAW_DATA_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="US")
    parser.add_argument("--category", default="0")  # 0 = all categories
    args = parser.parse_args()

    youtube = get_youtube_client()
    fetched_at = datetime.now(timezone.utc).isoformat()

    videos = fetch_trending(youtube, args.region, args.category)
    channel_ids = list({v["snippet"]["channelId"] for v in videos if "snippet" in v})
    channel_stats = fetch_channel_stats(youtube, channel_ids)

    rows = rows_from_api_response(videos, channel_stats, fetched_at)
    append_rows(rows)

    print(f"[{fetched_at}] appended {len(rows)} snapshot rows -> {RAW_DATA_PATH}")


if __name__ == "__main__":
    main()
