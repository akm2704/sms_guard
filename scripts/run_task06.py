"""Optional non-Jupyter command-line verification of task 6.

Run from project root: python scripts/run_task06.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from ml.features import make_sms_features_pipeline  # noqa: E402


def main():
    df = pd.read_csv(BASE_DIR / "data/processed/sms_clean.csv", keep_default_na=False)
    info = json.loads((BASE_DIR / "data/processed/sms_split.json").read_text(encoding="utf-8"))

    splits = {name: np.asarray(info[key], dtype=int) for name, key in (
        ("train", "train"), ("val", "validation"), ("test", "test"),
    )}
    sets = [set(indices) for indices in splits.values()]
    assert len(sets[0] | sets[1] | sets[2]) == len(df)
    assert sets[0].isdisjoint(sets[1])
    assert sets[0].isdisjoint(sets[2])
    assert sets[1].isdisjoint(sets[2])

    texts = {k: df.iloc[v]["text_raw"].fillna("") for k, v in splits.items()}
    y_train = df.iloc[splits["train"]]["label"].values
    pipeline = make_sms_features_pipeline()

    X_train = pipeline.fit_transform(texts["train"])  # fit only here!
    X_val = pipeline.transform(texts["val"])
    X_test = pipeline.transform(texts["test"])

    print("Train:", X_train.shape, "Validation:", X_val.shape, "Test:", X_test.shape)
    assert X_train.shape[0] == len(splits["train"])
    assert X_val.shape[0] == len(splits["val"])
    assert X_test.shape[0] == len(splits["test"])
    assert X_train.shape[1] == X_val.shape[1] == X_test.shape[1]

    vectorizer = pipeline.named_steps["features"].named_transformers["words"].named_steps["tfidf"]
    word_matrix = pipeline.named_steps["features"].named_transformers["words"].transform(texts["train"])
    words = vectorizer.get_feature_names_out()
    for klass, name in [(0, "Обычные SMS"), (1, "Спам-SMS")]:
        means = np.asarray(word_matrix[y_train == klass].mean(axis=0)).ravel()
        top = np.argsort(means)[-15:][::-1]
        print(f"\nТоп-15 среднего TF-IDF ({name}; только train):")
        for i in top:
            print(f"  {words[i]:24s} {means[i]:.4f}")

    print("\nОК: векторизатор обучен только на train, test не использован для fit.")


if __name__ == "__main__":
    main()
