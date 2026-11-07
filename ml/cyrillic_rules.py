"""Conservative rule-based demo for Cyrillic SMS.

Important: NOT a trained Russian/Kazakh classifier; does not output P(spam).
The custom_ru_kk.csv file is a test set per the assignment and is not
used for training by this module.
"""

from ml.preprocessing import normalize_sms
from ml.rules import detect_se_groups

GROUP_TITLES = {
    "URGENCY": "Призыв к срочному действию",
    "MONEY_TRANSFER": "Упоминание перевода или оплаты",
    "BANK_CARD": "Упоминание банка или карты",
    "ACCOUNT_BLOCK": "Угроза блокировки аккаунта",
    "PRIZE": "Обещание выигрыша или бонуса",
    "CODE_REQUEST": "Запрос кода или пароля",
}


def analyze_cyrillic_sms(text: str) -> dict:
    """Return signals, without calling the English ML model or URL services."""
    normalized = normalize_sms(text)
    groups = detect_se_groups(text)
    reasons = [GROUP_TITLES.get(group, group) for group in groups]

    has_url = "<url>" in normalized
    has_money = "<money>" in normalized
    has_phone = "<phone>" in normalized

    if has_url:
        reasons.append("Обнаружена ссылка (её безопасность не проверялась)")
    if has_money:
        reasons.append("Обнаружена денежная сумма")
    if has_phone:
        reasons.append("Обнаружен телефонный номер")

    # Risk indicators are not equal to classification: a benign text can
    # contain a phone, currency, or a link. We only warn about signals.
    return {
        "attention": bool(groups or has_url),
        "reasons": reasons,
    }
