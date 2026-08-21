import os
from pathlib import Path

# Locally: backend/app/core/config.py -> repo root is 3 parents up.
# In Docker: the Dockerfile copies backend/app straight to ./app (dropping
# the "backend/" level), so that same parents[3] math lands on "/" instead
# of the repo root. APP_BASE_DIR is set explicitly in the Dockerfile so this
# doesn't have to guess across two different folder layouts.
_env_base = os.environ.get("APP_BASE_DIR")
BASE_DIR = Path(_env_base) if _env_base else Path(__file__).resolve().parents[3]

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

MODELS_DIR = BASE_DIR / "ml" / "models"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

# app/db is always a direct sibling of app/core, regardless of how many
# levels up the repo root sits in either layout above — so this is computed
# independently of BASE_DIR and doesn't break in Docker.
DB_PATH = Path(__file__).resolve().parents[1] / "db" / "app.db"

DEPLOY_TIME = os.environ.get("DEPLOY_TIME", "")  # set by CI/CD on deploy
GIT_COMMIT_SHA = os.environ.get("GIT_COMMIT_SHA", "")