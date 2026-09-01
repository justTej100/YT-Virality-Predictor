import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

sys.path.append(str(Path(__file__).resolve().parents[3]))  # repo root, for `common`
from common.ensemble import compute_recency_weights  # noqa: E402
from common.feature_engineering import (  # noqa: E402
    build_feature_vector,
    feature_dict_to_vector,
    full_feature_name_list,
)

from app.core.config import MODEL_METADATA_PATH, MODELS_DIR


class Predictor:
    """
    Loads every model currently in the "council" (per model_metadata.json's
    council_versions, written by ml/train.py) and combines their votes at
    prediction time, weighted slightly toward more recent members. Reloading
    is cheap, so a fresh instance re-reads the latest council on every
    process start - this is how a new deploy picks up a newly trained/
    evicted membership without any special code path.
    """

    def __init__(self):
        self.council: list[dict] = []
        self._load()

    def _load(self) -> None:
        if not MODEL_METADATA_PATH.exists():
            return
        with open(MODEL_METADATA_PATH) as f:
            metadata = json.load(f)

        council_versions = metadata.get("council_versions", [])  # oldest -> newest
        versions_by_num = {v["version"]: v for v in metadata.get("versions", [])}
        weights = compute_recency_weights(len(council_versions))

        council = []
        for version, weight in zip(council_versions, weights):
            entry = versions_by_num.get(version)
            if not entry or not entry.get("model_file"):
                continue
            model = joblib.load(MODELS_DIR / entry["model_file"])
            council.append(
                {
                    "version": version,
                    "model": model,
                    "explainer": shap.TreeExplainer(model),
                    "weight": weight,
                    "accuracy": entry["metrics"]["accuracy"],
                    "trained_at": entry.get("trained_at"),
                }
            )
        self.council = council

    def is_ready(self) -> bool:
        return len(self.council) > 0

    @property
    def version(self) -> int | None:
        """Newest (highest-weighted) council member - used for logging."""
        return self.council[-1]["version"] if self.council else None

    @property
    def accuracy(self) -> float | None:
        return self.council[-1]["accuracy"] if self.council else None

    @property
    def trained_at(self) -> str | None:
        return self.council[-1]["trained_at"] if self.council else None

    def predict(self, video_record: dict) -> dict:
        if not self.is_ready():
            raise RuntimeError("No council members are currently loaded.")

        feature_dict = build_feature_vector(video_record)
        feature_names = full_feature_name_list()
        # A DataFrame with the same column names/order used at training time,
        # not a bare array - avoids sklearn's "X does not have valid feature
        # names" warning and keeps SHAP's feature attribution aligned to name.
        vector = pd.DataFrame([feature_dict_to_vector(feature_dict)], columns=feature_names)

        weighted_proba = 0.0
        weighted_shap = [0.0] * len(feature_names)
        votes = []

        for member in self.council:
            proba = float(member["model"].predict_proba(vector)[0][1])
            weighted_proba += proba * member["weight"]
            votes.append(
                {
                    "version": member["version"],
                    "probability": round(proba * 100, 1),
                    "weight": round(member["weight"], 3),
                }
            )

            # Per-feature contribution to this model's own prediction, in
            # log-odds space (TreeExplainer's exact, no-background-data mode
            # for tree ensembles). Combined across the council using the
            # same weights used for the vote itself - an approximation of
            # "the council's combined lean," not a rigorously joint value,
            # since each model's log-odds scale isn't perfectly comparable
            # to the others'. Good enough to show real relative direction
            # and rank of what mattered, which is the point.
            shap_row = member["explainer"].shap_values(vector)[0]
            for i, val in enumerate(shap_row):
                weighted_shap[i] += val * member["weight"]

        score = round(weighted_proba * 100, 1)
        if score >= 70:
            label = "High"
        elif score >= 40:
            label = "Medium"
        else:
            label = "Low"

        top = sorted(zip(feature_names, weighted_shap), key=lambda x: abs(x[1]), reverse=True)[:5]
        explanation = [
            {
                "feature": name,
                "contribution": round(float(val), 4),
                "direction": "up" if val > 0 else "down",
            }
            for name, val in top
        ]

        return {
            "score": score,
            "label": label,
            "features": feature_dict,
            "council_votes": votes,
            "explanation": explanation,
        }


# Singleton loaded once per process (per container / worker)
predictor = Predictor()