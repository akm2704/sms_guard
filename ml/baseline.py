"""Task 7: use the locally trained baseline SMS model."""
from functools import lru_cache
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "sms_baseline.joblib"


@lru_cache(maxsize=1)
def _load_model():
    """Load once per process. Only load a model created by your own trusted code."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Модель не найдена: {MODEL_PATH}. "
            "Сначала запустите scripts/train_sms_baseline.py"
        )
    return joblib.load(MODEL_PATH)


def predict_sms(text: str) -> dict:
    """Predict spam probability for a NEW raw SMS string, via saved pipeline."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Введите непустой текст SMS")
    if len(text) > 1000:
        raise ValueError("Длина SMS не должна превышать 1000 символов")

    model = _load_model()
    # The pipeline includes normalize_sms; DON'T normalize again here.
    probability = float(model.predict_proba([text])[0, list(model.classes_).index(1)])
    label = int(model.predict([text])[0])
    return {"label": label, "probability": round(probability, 4)}
