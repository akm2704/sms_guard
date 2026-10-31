from ml.preprocessing import normalize_sms


def test_empty_sms():
    assert normalize_sms("") == ""


def test_spaces_only():
    assert normalize_sms("    ") == ""


def test_url():
    text = "https://example.com/test"

    result = normalize_sms(text)

    assert result == "<url>"


def test_lowercase():
    text = "HELLO WORLD"

    result = normalize_sms(text)

    assert result == "hello world"


def test_russian_text():
    text = "ПрИвЕт МиР"

    result = normalize_sms(text)

    assert result == "привет мир"


def test_kazakh_letters():
    text = "ӘҒҚҢӨҰҮҺІ"

    result = normalize_sms(text)

    assert result == "әғқңөұүһі"


def test_money():
    text = "Переведите 5000 ₸"

    result = normalize_sms(text)

    assert "<money>" in result


def test_phone():
    text = "Позвоните +7 (777) 123-45-67"

    result = normalize_sms(text)

    assert "<phone>" in result


def test_email():
    text = "Пишите на user@example.com"

    result = normalize_sms(text)

    assert "<email>" in result


def test_numbers():
    text = "Ваш код 1234"

    result = normalize_sms(text)

    assert "<num>" in result


def test_emoji():
    text = "Привет 👋 мир!"

    result = normalize_sms(text)

    assert "привет" in result
    assert "мир" in result


def test_exclamation_marks():
    text = "СРОЧНО!!!"

    result = normalize_sms(text)

    assert result == "срочно!!!"


def test_multiple_spaces():
    text = "Привет     как     дела"

    result = normalize_sms(text)

    assert result == "привет как дела"