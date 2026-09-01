"""
CI gate: this test fails (and therefore blocks the GitHub Actions deploy job)
if the council is empty, or if any member currently in it is somehow below
the accuracy threshold. Membership itself is enforced by ml/train.py at
write time (rejected models never join, evicted ones get removed) - this
test is the independent safety net confirming that actually held, not the
thing that enforces it.
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import MODEL_METADATA_PATH  # noqa: E402

MIN_ACCEPTABLE_ACCURACY = 0.60


def _load_metadata():
    assert MODEL_METADATA_PATH.exists(), "model_metadata.json not found - run ml/train.py first."
    with open(MODEL_METADATA_PATH) as f:
        return json.load(f)


def test_council_is_not_empty():
    metadata = _load_metadata()
    council_versions = metadata.get("council_versions", [])
    assert len(council_versions) > 0, "No council members - every trained version failed the accuracy gate."


def test_council_does_not_exceed_its_size_limit():
    metadata = _load_metadata()
    council_versions = metadata.get("council_versions", [])
    council_size = metadata.get("council_size", 5)
    assert len(council_versions) <= council_size, (
        f"Council has {len(council_versions)} members but council_size is {council_size} - "
        f"eviction should have kept it at or under the limit."
    )


def test_every_council_member_meets_accuracy_threshold():
    metadata = _load_metadata()
    council_versions = set(metadata.get("council_versions", []))
    versions_by_num = {v["version"]: v for v in metadata["versions"]}

    for version in council_versions:
        entry = versions_by_num[version]
        accuracy = entry["metrics"]["accuracy"]
        assert accuracy >= MIN_ACCEPTABLE_ACCURACY, (
            f"Council member v{version} accuracy {accuracy} is below the "
            f"{MIN_ACCEPTABLE_ACCURACY} threshold - it should have been evicted or never admitted."
        )