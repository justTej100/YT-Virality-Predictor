"""
Trains the "viral growth potential" classifier and saves a versioned model
artifact + metadata file (a lightweight model registry).

Usage:
    python ml/train.py
    python ml/train.py --data ml/data/processed/training_data.csv

Produces:
    ml/models/model_vN.pkl
    ml/models/model_metadata.json   <- backend reads this to show model
                                        version/accuracy on the dashboard
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

# Minimum accuracy required to accept a newly trained model. This is the gate
# a CI pipeline checks before allowing a deploy - if a retrain produces a
# worse model (e.g. due to a data quality issue), the deploy is blocked and
# the previously-deployed model stays live.
MIN_ACCEPTABLE_ACCURACY = 0.60


def next_version_number() -> int:
    if not METADATA_PATH.exists():
        return 1
    with open(METADATA_PATH) as f:
        history = json.load(f)
    return history.get("current_version", 0) + 1


def load_metadata_history() -> dict:
    if METADATA_PATH.exists():
        with open(METADATA_PATH) as f:
            return json.load(f)
    return {"current_version": 0, "versions": []}


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


def save_model_and_metadata(model, metrics: dict, n_train: int, n_test: int, data_path: Path) -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    version = next_version_number()
    model_path = MODELS_DIR / f"model_v{version}.pkl"
    joblib.dump(model, model_path)

    history = load_metadata_history()
    history["current_version"] = version
    history["current_model_file"] = model_path.name
    entry = {
        "version": version,
        "model_file": model_path.name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_data": str(data_path),
        "n_train_rows": n_train,
        "n_test_rows": n_test,
        "metrics": metrics,
        "feature_names": full_feature_name_list(),
        "accepted": metrics["accuracy"] >= MIN_ACCEPTABLE_ACCURACY,
    }
    history.setdefault("versions", []).append(entry)

    if not entry["accepted"]:
        # Roll back: don't let CI/CD treat this as the deployable version.
        history["current_version"] = version - 1 if version > 1 else 0
        if history["current_version"] > 0:
            prev = next(v for v in history["versions"] if v["version"] == history["current_version"])
            history["current_model_file"] = prev["model_file"]
        else:
            history["current_model_file"] = None

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

    print(f"Saved model -> {model_path}")
    print(f"Metrics: {result['metrics']}")
    if result["metrics"]["accuracy"] < MIN_ACCEPTABLE_ACCURACY:
        print(
            f"WARNING: accuracy {result['metrics']['accuracy']} is below the "
            f"{MIN_ACCEPTABLE_ACCURACY} deploy threshold. This version will "
            f"NOT be marked as the deployable model."
        )
        sys.exit(2)  # non-zero exit -> fails CI step, blocks deploy


if __name__ == "__main__":
    main()
