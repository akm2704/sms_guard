from pathlib import Path
import csv

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

RAW_PATH = BASE_DIR / "data" / "raw" / "SMSSpamCollection"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "sms_raw.csv"


def load_sms():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Файл датасета не найден: {RAW_PATH}"
        )

    # Проверяем кодировку исходного файла.
    for encoding in ("utf-8", "latin-1"):
        try:
            df = pd.read_csv(
                RAW_PATH,
                sep="\t",
                header=None,
                names=["label", "text"],
                encoding=encoding,
                quoting=csv.QUOTE_NONE,
                keep_default_na=False,
            )
            print(f"Кодировка файла: {encoding}")
            break

        except UnicodeDecodeError:
            continue

    # Проверка исходных категорий.
    labels = set(df["label"].unique())

    if not labels.issubset({"ham", "spam"}):
        raise ValueError(
            f"Неизвестные категории: {labels}"
        )

    # Преобразование категорий в числа.
    df["label"] = df["label"].map({
        "ham": 0,
        "spam": 1,
    })

    # Добавляем уникальный идентификатор.
    df.insert(0, "id", range(1, len(df) + 1))

    return df


def main():
    df = load_sms()
    return df[["id", "text", "label"]]

    print("\n=== ОБЩАЯ ИНФОРМАЦИЯ ===")
    print("Количество SMS:", len(df))

    print("\n=== ТИПЫ ДАННЫХ ===")
    print(df.dtypes)

    print("\n=== РАСПРЕДЕЛЕНИЕ КЛАССОВ ===")
    print(df["label"].value_counts())

    print("\n=== БАЛАНС КЛАССОВ (%) ===")
    print(
        df["label"].value_counts(normalize=True) * 100
    )

    print("\n=== ПРИМЕРЫ ОБЫЧНЫХ SMS ===")
    print(
        df[df["label"] == 0].head(5).to_string(index=False)
    )

    print("\n=== ПРИМЕРЫ СПАМ-SMS ===")
    print(
        df[df["label"] == 1].head(5).to_string(index=False)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print("\nДатасет сохранён:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()