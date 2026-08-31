"""
CI gate: this test fails (and therefore blocks the GitHub Actions deploy job)
if the currently-accepted model's recorded accuracy is below threshold, or if
no accepted model exists at all. This is what makes accuracy-gated deploys
real rather than just a talking point.
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import MODEL_METADATA_PATH  # noqa: E402

MIN_ACCEPTABLE_ACCURACY = 0.60


def test_current_model_meets_accuracy_threshold():
    assert MODEL_METADATA_PATH.exists(), "model_metadata.json not found - run ml/train.py first."

    with open(MODEL_METADATA_PATH) as f:
        metadata = json.load(f)

    current_version = metadata.get("current_version", 0)
    assert current_version > 0, "No accepted model version - all trained versions failed the accuracy gate."

    entry = next(v for v in metadata["versions"] if v["version"] == current_version)
    accuracy = entry["metrics"]["accuracy"]

    assert accuracy >= MIN_ACCEPTABLE_ACCURACY, (
        f"Current model v{current_version} accuracy {accuracy} is below "
        f"the {MIN_ACCEPTABLE_ACCURACY} deploy threshold."
    )
