from fastapi import APIRouter

from app.models.predictor import predictor

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok" if predictor.is_ready() else "degraded_no_model",
        "model_loaded": predictor.is_ready(),
    }
