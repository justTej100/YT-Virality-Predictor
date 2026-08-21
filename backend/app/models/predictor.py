import json
import sys
from pathlib import Path

import joblib

sys.path.append(str(Path(__file__).resolve().parents[3]))  # repo root, for `common`
from common.feature_engineering import build_feature_vector, feature_dict_to_vector  # noqa: E402

from app.core.config import MODEL_METADATA_PATH, MODELS_DIR


class Predictor:
    """
    Loads the currently-accepted model version (per model_metadata.json,
    written by ml/train.py) and serves predictions. Reloading is cheap, so a
    fresh instance re-reads the latest accepted model on every process start
    - this is how a new deploy picks up a newly trained model without any
    special code path.
    """

    def __init__(self):
        self.model = None
        self.version: int | None = None
        self.trained_at: str | None = None
        self.accuracy: float | None = None
        self._load()

    def _load(self) -> None:
        if not MODEL_METADATA_PATH.exists():
            return
        with open(MODEL_METADATA_PATH) as f:
            metadata = json.load(f)

        model_file = metadata.get("current_model_file")
        if not model_file:
            return

        version_entry = next(
            (v for v in metadata.get("versions", []) if v["model_file"] == model_file), None
        )

        self.model = joblib.load(MODELS_DIR / model_file)
        self.version = metadata.get("current_version")
        if version_entry:
            self.trained_at = version_entry.get("trained_at")
            self.accuracy = version_entry.get("metrics", {}).get("accuracy")

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, video_record: dict) -> dict:
        if not self.is_ready():
            raise RuntimeError("No accepted model is currently loaded.")

        feature_dict = build_feature_vector(video_record)
        vector = [feature_dict_to_vector(feature_dict)]

        # predict_proba -> probability of class 1 ("will grow"), scaled to 0-100
        proba = self.model.predict_proba(vector)[0][1]
        score = round(proba * 100, 1)

        if score >= 70:
            label = "High"
        elif score >= 40:
            label = "Medium"
        else:
            label = "Low"

        return {"score": score, "label": label, "features": feature_dict}


# Singleton loaded once per process (per container / worker)
predictor = Predictor()
