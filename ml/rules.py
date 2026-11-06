"""Минимальные группы признаков социальной инженерии для заданий 6–7.

В задании 12 словарь будет расширен и отдельно протестирован по языкам.
"""

from ml.preprocessing import normalize_sms

SOCIAL_ENGINEERING_GROUPS = {
    "URGENCY": (
        "urgent", "immediately", "asap", "act now", "within 24 hours",
        "срочно", "немедленно", "только сегодня", "в течение 24 часов",
        "шұғыл", "жедел", "тез арада", "бүгін",
    ),
    "MONEY_TRANSFER": (
        "transfer", "send money", "pay now", "payment required", "cash",
        "переведи", "переведите", "перевод", "оплатите", "деньги",
        "ақша", "аударыңыз", "төлем", "төлеңіз",
    ),
    "BANK_CARD": (
        "bank", "credit card", "debit card", "card details", "account number",
        "банк", "карта", "банковский", "реквизиты", "касpi", "халык",
        "банк картаңыз", "картаңыз", "банктік", "шот",
    ),
    "ACCOUNT_BLOCK": (
        "blocked", "locked", "suspended", "account closure", "disabled",
        "заблокирована", "заблокирован", "блокировка", "отключен", "заморожен",
        "бұғатталды", "бұғатталған", "жабылады", "тоқтатылды",
    ),
    "PRIZE": (
        "prize", "winner", "won", "congratulations", "reward", "free gift",
        "выигрыш", "приз", "победитель", "поздравляем", "бонус",
        "ұтыс", "сыйлық", "жеңімпаз", "құттықтаймыз", "жүлде",
    ),
    "CODE_REQUEST": (
        "send your code", "share the code", "tell us your code", "verification code", "password",
        "сообщите код", "назовите код", "передайте код", "пароль", "код подтверждения",
        "кодты айтыңыз", "растау коды", "құпия сөз", "кодты жіберіңіз",
    ),
}

# Предварительное исключение очевидных защитных предупреждений.
# Не заменяет полноценную контекстную модель или проверку правил задания 12.
CODE_WARNING_PHRASES = (
    "никому не сообщайте", "не передавайте код", "do not share your code",
    "never share your code", "ешкімге айтпаңыз", "кодты ешкімге бермеңіз",
)


def detect_se_groups(text: str) -> list[str]:
    """Возвращает названия групп, найденных в тексте; без сетевых запросов."""
    clean = normalize_sms(text)
    found = []
    for group, phrases in SOCIAL_ENGINEERING_GROUPS.items():
        if group == "CODE_REQUEST" and any(warning in clean for warning in CODE_WARNING_PHRASES):
            continue
        if any(phrase.lower() in clean for phrase in phrases):
            found.append(group)
    return found
