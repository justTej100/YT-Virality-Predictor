"""
Trains a candidate "viral growth potential" classifier. If it clears the
accuracy gate, it joins a rolling council of up to COUNCIL_SIZE models
(model_metadata.json is the registry) that vote together at serving time,
weighted slightly toward more recent members. If joining pushes the council
over capacity, whichever member has the lowest accuracy is evicted and its
.pkl file deleted - so at most COUNCIL_SIZE model files ever exist on disk.

Usage:
    python ml/train.py
    python ml/train.py --data ml/data/processed/training_data.csv
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.feature_engineering import full_feature_name_list  # noqa: E402

MODELS_DIR = Path(__file__).resolve().parent / "models"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "processed" / "training_data.csv"

# Local, file-based MLflow tracking store - no server to run or host.
# `mlflow ui --backend-store-uri ml/mlruns` opens a dashboard over everything
# logged here: params, metrics, and the model artifact for every run, so you
# can compare versions instead of reading model_metadata.json by eye.
# This is purely for experiment visibility - it doesn't change what gets
# deployed. That's still decided by model_metadata.json + the accuracy gate
# below and in backend/tests/test_model_accuracy.py, exactly as before.
MLRUNS_DIR = Path(__file__).resolve().parent / "mlruns"
mlflow.set_tracking_uri(f"file:{MLRUNS_DIR}")
mlflow.set_experiment("yt-virality-predictor")

# Minimum accuracy required for a newly trained model to be eligible to join
# the council at all. Below this, the model is rejected outright - never
# saved to disk, never considered for membership. This is the gate a CI
# pipeline checks before allowing a deploy.
MIN_ACCEPTABLE_ACCURACY = 0.60

# How many models are allowed to vote at once. Once an accepted model would
# push membership past this, whichever member - old or new - has the lowest
# accuracy gets evicted, and its .pkl file is deleted from disk. This keeps
# exactly COUNCIL_SIZE model files on disk/in git, never more.
COUNCIL_SIZE = 5


def load_metadata_history() -> dict:
    if METADATA_PATH.exists():
        with open(METADATA_PATH) as f:
            return json.load(f)
    return {"council_size": COUNCIL_SIZE, "council_versions": [], "next_version": 1, "versions": []}


def train(data_path: Path) -> dict:
    df = pd.read_csv(data_path)
    feature_cols = full_feature_name_list()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Training data is missing expected feature columns: {missing}")

    X = df[feature_cols]
    y = df["label_will_grow"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    hyperparams = {"n_estimators": 150, "max_depth": 3, "learning_rate": 0.08, "random_state": 42}

    with mlflow.start_run():
        mlflow.log_params(hyperparams)
        mlflow.log_param("training_data", str(data_path))
        mlflow.log_param("n_train_rows", len(X_train))
        mlflow.log_param("n_test_rows", len(X_test))

        model = GradientBoostingClassifier(**hyperparams)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": round(accuracy_score(y_test, preds), 4),
            "f1_score": round(f1_score(y_test, preds), 4),
            "roc_auc": round(roc_auc_score(y_test, probs), 4),
        }
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")

    return {"model": model, "metrics": metrics, "n_train": len(X_train), "n_test": len(X_test)}


def save_model_and_metadata(model, metrics: dict, n_train: int, n_test: int, data_path: Path) -> Path | None:
    """
    Registers a newly trained model. Returns the saved .pkl path if it
    joined the council, or None if it was rejected by the accuracy gate
    (in which case nothing is written to disk except the metadata record
    of the rejection, for audit history).
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    history = load_metadata_history()

    version = history.get("next_version", 1)
    history["next_version"] = version + 1
    accepted = metrics["accuracy"] >= MIN_ACCEPTABLE_ACCURACY

    entry = {
        "version": version,
        "model_file": None,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_data": str(data_path),
        "n_train_rows": n_train,
        "n_test_rows": n_test,
        "metrics": metrics,
        "feature_names": full_feature_name_list(),
        "accepted": accepted,
        "in_council": False,
    }
    history.setdefault("versions", []).append(entry)

    if not accepted:
        # Never clears the gate -> never touches disk, never joins the
        # council. The rejection itself is still recorded above for history.
        with open(METADATA_PATH, "w") as f:
            json.dump(history, f, indent=2)
        return None

    model_path = MODELS_DIR / f"model_v{version}.pkl"
    joblib.dump(model, model_path)
    entry["model_file"] = model_path.name
    entry["in_council"] = True
    history.setdefault("council_versions", []).append(version)

    # Over capacity? Evict whichever member - old or new - has the lowest
    # accuracy, and delete its file. Loops in case council_size was lowered.
    council_size = history.get("council_size", COUNCIL_SIZE)
    versions_by_num = {v["version"]: v for v in history["versions"]}
    while len(history["council_versions"]) > council_size:
        members = [versions_by_num[v] for v in history["council_versions"]]
        worst = min(members, key=lambda v: v["metrics"]["accuracy"])

        worst_path = MODELS_DIR / worst["model_file"]
        if worst_path.exists():
            worst_path.unlink()

        worst["in_council"] = False
        worst["evicted_at"] = datetime.now(timezone.utc).isoformat()
        worst["model_file"] = None
        history["council_versions"].remove(worst["version"])

    with open(METADATA_PATH, "w") as f:
        json.dump(history, f, indent=2)

    return model_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    args = parser.parse_args()

    if not args.data.exists():
        print(
            f"Training data not found at {args.data}.\n"
            f"Run ml/data/generate_synthetic_data.py first, or accumulate "
            f"real data with ml/ingestion/poll_trending.py."
        )
        sys.exit(1)

    result = train(args.data)
    model_path = save_model_and_metadata(
        result["model"], result["metrics"], result["n_train"], result["n_test"], args.data
    )

    print(f"Metrics: {result['metrics']}")
    if model_path is None:
        print(
            f"REJECTED: accuracy {result['metrics']['accuracy']} is below the "
            f"{MIN_ACCEPTABLE_ACCURACY} gate. Not saved, not added to the council."
        )
        sys.exit(2)  # non-zero exit -> fails CI step, blocks deploy

    print(f"Saved model -> {model_path} (joined the council)")


if __name__ == "__main__":
    main()