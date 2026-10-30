
from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "learnpath_student_model.joblib"

_model_bundle = None


def _load_model():
    global _model_bundle

    if _model_bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found: {MODEL_PATH}"
            )
        _model_bundle = joblib.load(MODEL_PATH)

    return _model_bundle


def predict_next_success(student_features: dict) -> dict:
    """Predict course outcome only when the correct OULAD features exist."""

    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    missing_features = [
        name for name in feature_columns
        if name not in student_features
    ]

    if missing_features:
        return {
            "available": False,
            "message": (
                "The trained model predicts OULAD course outcomes, "
                "but this student's quiz history uses different features. "
                "A quiz-specific model is needed for a valid prediction."
            ),
        }

    frame = pd.DataFrame(
        [{name: student_features[name] for name in feature_columns}],
        columns=feature_columns,
    )

    prediction = str(model.predict(frame)[0])
    result = {
        "available": True,
        "predicted_result": prediction,
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(frame)[0]
        result["probabilities"] = {
            str(label): round(float(probability), 4)
            for label, probability in zip(model.classes_, probabilities)
        }

    return result
