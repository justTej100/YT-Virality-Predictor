"""
Generates a synthetic labeled training set so you can train + deploy a
working model IMMEDIATELY, without waiting for hours of real polling data to
accumulate via poll_trending.py.

This is a legitimate, common practice: bootstrap with synthetic/seed data,
then swap in real accumulated snapshots (ml/data/raw/snapshots.csv, processed
via build_training_set_from_snapshots.py) once you have enough. Be upfront
about this in your README - it's honest and still demonstrates the full
pipeline.

Usage:
    python ml/data/generate_synthetic_data.py --n 3000
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.feature_engineering import build_feature_vector, full_feature_name_list  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent / "processed" / "training_data.csv"

CATEGORY_IDS = ["1", "2", "10", "15", "17", "19", "20", "22", "23", "24", "25", "26", "27", "28"]

TITLE_TEMPLATES = [
    "I Tried {x} For 30 Days",
    "The Truth About {x}",
    "{x} Explained in 10 Minutes",
    "Why Everyone Is Wrong About {x}",
    "My {x} Setup 2026",
    "{x} vs {y} - Which Is Better?",
    "How I Built {x}",
    "Reacting to {x}",
    "{x} Tier List",
    "This {x} Video Went Viral",
]

WORDS = ["AI", "Coding", "Fitness", "Cooking", "Gaming", "Travel", "Finance", "Minecraft", "Startups", "Music"]


def random_title() -> str:
    template = random.choice(TITLE_TEMPLATES)
    return template.format(x=random.choice(WORDS), y=random.choice(WORDS))


def synthesize_video(rng: random.Random) -> tuple[dict, float]:
    """Returns (raw_video_record, label) where label = future 6h view growth rate."""
    subscriber_count = int(rng.lognormvariate(9, 2.2))  # heavy-tailed, most small, some huge
    channel_video_count = rng.randint(5, 3000)
    hours_since_upload = rng.uniform(0.2, 72)

    # Simulate "true" underlying popularity that drives both current views
    # AND future growth - this is what the model has to learn to approximate
    # from observable proxies (title, category, subs, early velocity).
    popularity_signal = (
        rng.gauss(0, 1)
        + 0.6 * (subscriber_count > 500_000)
        + 0.4 * (hours_since_upload < 6)
        - 0.3 * (hours_since_upload > 48)
    )

    base_view_rate = max(rng.lognormvariate(3 + 0.8 * popularity_signal, 1.1), 1)
    view_count = int(base_view_rate * hours_since_upload)
    like_count = int(view_count * max(rng.gauss(0.045, 0.02), 0.001))
    comment_count = int(view_count * max(rng.gauss(0.006, 0.004), 0.0))

    duration_seconds = rng.choice([rng.randint(20, 59), rng.randint(60, 1200)])
    tags = [f"tag{i}" for i in range(rng.randint(0, 15))]

    published_at = (
        datetime.now(timezone.utc) - timedelta(hours=hours_since_upload)
    ).isoformat()
    fetched_at = datetime.now(timezone.utc).isoformat()

    record = {
        "published_at": published_at,
        "fetched_at": fetched_at,
        "view_count": view_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "title": random_title(),
        "tags": tags,
        "category_id": rng.choice(CATEGORY_IDS),
        "duration": f"PT{duration_seconds}S",
        "subscriber_count": subscriber_count,
        "channel_video_count": channel_video_count,
    }

    # Label: will this video's views grow >50% in the next 6 hours?
    # Higher popularity_signal + early stage + already-decent velocity -> more likely.
    growth_logit = (
        0.9 * popularity_signal
        + 0.5 * (hours_since_upload < 12)
        - 0.02 * hours_since_upload
        + rng.gauss(0, 0.8)
    )
    will_grow = 1.0 if growth_logit > 0.4 else 0.0

    return record, will_grow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    rows = []
    for _ in range(args.n):
        record, label = synthesize_video(rng)
        features = build_feature_vector(record)
        features["label_will_grow"] = label
        features["_title"] = record["title"]  # kept for debugging, dropped before training
        rows.append(features)

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df)} synthetic rows -> {OUTPUT_PATH}")
    print(f"Feature columns: {full_feature_name_list()}")


if __name__ == "__main__":
    main()
