import re
import unicodedata


# Регулярное выражение для электронной почты
EMAIL_PATTERN = re.compile(
    r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b",
    re.IGNORECASE
)


# Регулярное выражение для URL
URL_PATTERN = re.compile(
    r"(?:https?://|www\.)[^\s<>]+",
    re.IGNORECASE
)


# Регулярное выражение для денежных сумм
MONEY_PATTERN = re.compile(
    r"(?<!\w)(?:[$£₸]\s*\d[\d\s.,]*|"
    r"\d[\d\s.,]*\s*(?:₸|тг|тенге|"
    r"руб(?:лей|ля|ль)?\.?|kzt|usd))(?!\w)",
    re.IGNORECASE
)


# Регулярное выражение для телефонов
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d[\d() .-]{8,}\d)(?!\w)"
)


# Регулярное выражение для чисел
NUMBER_PATTERN = re.compile(
    r"(?<![\w<>])\d+(?:[.,]\d+)*(?![\w<>])"
)


def replace_phone(match):
    """
    Заменяет телефон на <phone>.

    Телефон должен содержать
    от 10 до 15 цифр.
    """

    number = match.group(0)

    digit_count = sum(
        char.isdigit()
        for char in number
    )

    if 10 <= digit_count <= 15:
        return " <phone> "

    return number


def normalize_sms(text, stopwords=None):
    """
    Нормализация SMS-сообщения.

    Выполняет:
    1. Unicode-нормализацию.
    2. Приведение к нижнему регистру.
    3. Удаление управляющих символов.
    4. Замену email, URL, сумм, телефонов и чисел.
    5. Удаление лишних символов и пробелов.
    6. Необязательное удаление стоп-слов.

    Возвращает очищенную строку.
    """

    # Обработка пустого значения
    if text is None:
        return ""

    if not isinstance(text, str):
        raise TypeError(
            "SMS должен быть строкой"
        )

    # Unicode NFKC и нижний регистр
    text = unicodedata.normalize(
        "NFKC", text
    ).lower()

    # Удаляем управляющие символы
    text = "".join(
        " "
        if unicodedata.category(char).startswith("C")
        else char
        for char in text
    )

    # Заменяем электронную почту
    text = EMAIL_PATTERN.sub(
        " <email> ", text
    )

    # Заменяем URL
    text = URL_PATTERN.sub(
        " <url> ", text
    )

    # Заменяем денежные суммы
    text = MONEY_PATTERN.sub(
        " <money> ", text
    )

    # Заменяем телефоны
    text = PHONE_PATTERN.sub(
        replace_phone, text
    )

    # Заменяем остальные числа
    text = NUMBER_PATTERN.sub(
        " <num> ", text
    )

    # Удаляем лишнюю пунктуацию,
    # но оставляем ! ? и токены <...>
    text = re.sub(
        r"[^\w\s<>!?]",
        " ",
        text
    )

    # Удаляем повторяющиеся пробелы
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Необязательное удаление стоп-слов
    if stopwords:
        text = " ".join(
            word
            for word in text.split()
            if word not in stopwords
        )

    return text