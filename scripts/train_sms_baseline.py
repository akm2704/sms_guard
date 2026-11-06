"""Task 7: train SMS baseline on TRAIN and evaluate on VALIDATION only.

Run from project root:
    .\\.venv\\Scripts\\python.exe scripts\\train_sms_baseline.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.features import make_sms_features_pipeline  # noqa: E402

DATA_PATH = ROOT / "data" / "processed" / "sms_clean.csv"
SPLIT_PATH = ROOT / "data" / "processed" / "sms_split.json"
MODEL_PATH = ROOT / "ml" / "artifacts" / "sms_baseline.joblib"
METRICS_PATH = ROOT / "docs" / "07_sms_baseline_metrics.json"
FIGURE_PATH = ROOT / "docs" / "figures" / "07_sms_baseline_confusion_matrix.png"


def _short_safe_text(value: object) -> str:
    """Shorten output and mask long digit sequences before writing to console."""
    text = re.sub(r"\d{5,}", "[NUM]", str(value))
    return text.replace("\n", " ")[:125]


def main():
    if not DATA_PATH.exists() or not SPLIT_PATH.exists():
        raise FileNotFoundError("Сначала завершите задание 6: нужны sms_clean.csv и sms_split.json")

    df = pd.read_csv(DATA_PATH, keep_default_na=False)
    split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    train_idx = np.asarray(split["train"], dtype=int)
    val_idx = np.asarray(split["validation"], dtype=int)
    test_idx = np.asarray(split["test"], dtype=int)

    # Treat TEST as sealed: check indices only, never fit or evaluate on test.
    n = len(df)
    if (len(set(train_idx)) != len(train_idx)
            or len(set(val_idx)) != len(val_idx)
            or len(set(test_idx)) != len(test_idx)
            or len(set(train_idx) | set(val_idx) | set(test_idx)) != n
            or not set(train_idx).isdisjoint(val_idx)
            or not set(train_idx).isdisjoint(test_idx)
            or not set(val_idx).isdisjoint(test_idx)):
        raise ValueError("Некорректное разбиение: пропущены, повторены или пересекаются индексы")

    X_train = df.iloc[train_idx]["text_raw"].fillna("").astype(str)
    y_train = df.iloc[train_idx]["label"].astype(int).to_numpy()
    X_val = df.iloc[val_idx]["text_raw"].fillna("").astype(str)
    y_val = df.iloc[val_idx]["label"].astype(int).to_numpy()

    # Normalization is INSIDE make_sms_features_pipeline(). Supply raw SMS text.
    model = Pipeline([
        ("features", make_sms_features_pipeline()),
        ("classifier", LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        )),
    ])

    print(f"Обучение LogisticRegression: train={len(X_train)}, validation={len(X_val)}")
    model.fit(X_train, y_train)  # only train!
    prob_spam = model.predict_proba(X_val)[:, list(model.classes_).index(1)]
    pred = model.predict(X_val)

    metrics = {
        "algorithm": "LogisticRegression",
        "random_state": 42,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "train_count": len(X_train),
        "validation_count": len(X_val),
        "test_count_not_used": len(test_idx),
        "accuracy": float(accuracy_score(y_val, pred)),
        "precision_spam": float(precision_score(y_val, pred, zero_division=0)),
        "recall_spam": float(recall_score(y_val, pred, zero_division=0)),
        "f1_spam": float(f1_score(y_val, pred, zero_division=0)),
        "confusion_matrix_0_1": confusion_matrix(y_val, pred, labels=[0, 1]).tolist(),
    }

    print("\n=== МЕТРИКИ НА VALIDATION (НЕ TEST) ===")
    for name in ("accuracy", "precision_spam", "recall_spam", "f1_spam"):
        print(f"{name}: {metrics[name]:.4f}")
    print("Матрица ошибок [[TN, FP], [FN, TP]]:")
    print(np.asarray(metrics["confusion_matrix_0_1"]))

    FN = np.flatnonzero((y_val == 1) & (pred == 0))
    FP = np.flatnonzero((y_val == 0) & (pred == 1))
    print(f"\nЛожноотрицательные (FN): {len(FN)}; ложноположительные (FP): {len(FP)}")
    for label, arr in (("FN — пропущенный спам", FN), ("FP — ложная тревога", FP)):
        print(f"\n{label}: до 5 примеров")
        for i in arr[:5]:
            print(f"  P(spam)={prob_spam[i]:.3f}: {_short_safe_text(X_val.iloc[int(i)])}")
        if len(arr) < 5:
            print(f"  Доступно только {len(arr)} таких ошибок; примеры не выдумываем.")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Joblib can execute code on load: load only locally generated trusted models.
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    disp = ConfusionMatrixDisplay(
        confusion_matrix=np.asarray(metrics["confusion_matrix_0_1"]),
        display_labels=["Обычные", "Спам"],
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title("SMS baseline — матрица ошибок (validation)")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=220)
    plt.close(fig)

    loaded = joblib.load(MODEL_PATH)  # trusted model, written just above
    check = loaded.predict(X_val.iloc[:10])
    assert np.array_equal(check, pred[:10]), "Предсказания после загрузки не совпадают!"

    print("\nМодель сохранена:", MODEL_PATH)
    print("Метрики сохранены:", METRICS_PATH)
    print("График сохранён:", FIGURE_PATH)
    print("Проверка сохранения и загрузки модели: OK")
    print("Тестовая выборка не использовалась.")


if __name__ == "__main__":
    main()
