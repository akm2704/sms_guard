from pathlib import Path
import sys

import pandas as pd


# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parents[2]

# Добавляем корень проекта в путь импорта
sys.path.insert(0, str(BASE_DIR))

from ml.preprocessing import normalize_sms


# Пути к файлам
INPUT_PATH = BASE_DIR / "data" / "processed" / "sms_raw.csv"

OUTPUT_PATH = BASE_DIR / "data" / "processed" / "sms_clean.csv"

REPORT_PATH = BASE_DIR / "docs" / "04_preprocessing_report.md"


def clean_dataset():

    print("=" * 55)
    print("SMS GUARD — ПРЕДВАРИТЕЛЬНАЯ ОБРАБОТКА")
    print("=" * 55)

    # 1. Проверка файла
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Не найден исходный файл: {INPUT_PATH}"
        )

    # 2. Загрузка датасета
    df = pd.read_csv(
        INPUT_PATH,
        encoding="utf-8",
        keep_default_na=False
    )

    required_columns = {"id", "text", "label"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "В датасете отсутствуют необходимые столбцы"
        )

    if not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError("Обнаружены неизвестные метки классов")

    original_count = len(df)

    print(f"\nИсходное количество SMS: {original_count}")

    # 3. Сохраняем исходный текст
    df["text_raw"] = df["text"].fillna("").astype(str)

    # 4. Нормализация сообщений
    print("\nВыполняется нормализация SMS...")

    df["text_clean"] = df["text_raw"].apply(
        normalize_sms
    )

    # 5. Считаем изменённые сообщения
    changed_count = (
        df["text_raw"] != df["text_clean"]
    ).sum()

    print(f"Нормализация изменила сообщений: {changed_count}")

    # 6. Удаляем пустые сообщения
    empty_mask = df["text_clean"].eq("")

    empty_by_class = (
        df.loc[empty_mask, "label"]
        .value_counts()
        .reindex([0, 1], fill_value=0)
    )

    empty_count = int(empty_mask.sum())

    df = df.loc[~empty_mask].copy()

    print(f"Удалено пустых сообщений: {empty_count}")

    # 7. Проверяем противоречия в разметке
    # Одинаковые очищенные тексты не должны
    # иметь разные метки классов.

    conflicting_groups = (
        df.groupby("text_clean")["label"]
        .nunique()
    )

    conflicting_texts = conflicting_groups[
        conflicting_groups > 1
    ]

    if not conflicting_texts.empty:
        print(
            "\nВНИМАНИЕ: обнаружены одинаковые "
            "тексты с разными метками!"
        )
        print(
            "Количество противоречивых текстов:",
            len(conflicting_texts)
        )

        raise ValueError(
            "Необходимо проверить противоречивую "
            "разметку перед удалением дубликатов."
        )

    # 8. Находим дубликаты
    duplicate_mask = df.duplicated(
        subset=["text_clean"],
        keep="first"
    )

    duplicates_by_class = (
        df.loc[duplicate_mask, "label"]
        .value_counts()
        .reindex([0, 1], fill_value=0)
    )

    duplicate_count = int(duplicate_mask.sum())

    # 9. Удаляем дубликаты
    df = df.loc[~duplicate_mask].copy()

    print(f"Удалено дубликатов: {duplicate_count}")

    print("\nДубликаты по категориям:")
    print(f"Обычные SMS: {duplicates_by_class[0]}")
    print(f"Спам-SMS: {duplicates_by_class[1]}")

    # 10. Оставляем необходимые столбцы
    df = df[
        ["id", "text_raw", "text_clean", "label"]
    ]

    # 11. Сохраняем результат
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    # 12. Отчёт
    report = f"""# Отчёт о предварительной обработке SMS

## 1. Общая информация

Проект: SMS Guard.

Исходный набор: UCI SMS Spam Collection.

Алгоритм: normalize_sms().

## 2. Результаты обработки

| Этап | Количество записей |
|---|---:|
| Исходный датасет | {original_count} |
| Сообщения, изменённые нормализацией | {changed_count} |
| Удалено пустых сообщений | {empty_count} |
| Удалено дубликатов | {duplicate_count} |
| Итоговое количество SMS | {len(df)} |

## 3. Удалённые записи по классам

| Причина | Обычные (0) | Спам (1) |
|---|---:|---:|
| Пустой текст | {empty_by_class[0]} | {empty_by_class[1]} |
| Дубликаты | {duplicates_by_class[0]} | {duplicates_by_class[1]} |

## 4. Применённые преобразования

1. Unicode-нормализация NFKC.
2. Приведение текста к нижнему регистру.
3. Замена URL на <url>.
4. Замена email на <email>.
5. Замена телефонов на <phone>.
6. Замена денежных сумм на <money>.
7. Замена чисел на <num>.
8. Удаление лишних пробелов.
9. Удаление пустых сообщений.
10. Удаление дубликатов по очищенному тексту.

## 5. Итог

После предварительной обработки получено {len(df)} SMS.

Результат сохранён в файле:

data/processed/sms_clean.csv

Данные готовы для следующего этапа —
исследовательского анализа (EDA).
"""

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_PATH.write_text(
        report,
        encoding="utf-8"
    )

    # 13. Итоговая статистика
    print("\n" + "=" * 55)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 55)

    print(f"Исходных SMS: {original_count}")
    print(f"Удалено пустых: {empty_count}")
    print(f"Удалено дубликатов: {duplicate_count}")
    print(f"Осталось SMS: {len(df)}")

    print("\nРаспределение классов:")
    print(df["label"].value_counts())

    print("\nПримеры очищенных SMS:")
    print(
        df[["text_raw", "text_clean"]]
        .head(5)
        .to_string(index=False)
    )

    print("\nФайл сохранён:")
    print(OUTPUT_PATH)

    print("\nОтчёт сохранён:")
    print(REPORT_PATH)

    return df


if __name__ == "__main__":
    clean_dataset()