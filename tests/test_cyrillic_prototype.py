"""Cyrillic routing tests: never misuse the English spam probability."""
from unittest.mock import patch

from django.urls import reverse

from ml.cyrillic_rules import analyze_cyrillic_sms


def test_ru_normal_no_english_model(client):
    with patch("apps.analysis.views.predict_sms") as english_model:
        response = client.post(reverse("sms-check"), {
            "text": "Напоминаю: Ваша встреча назначена на завтра в 14:00."
        })
    assert response.status_code == 200
    english_model.assert_not_called()
    html = response.content.decode("utf-8")
    assert "Явных тревожных признаков" in html
    assert "вероятность спама не вычисляется" in html
    assert "88.11%" not in html


def test_kazakh_normal_no_english_model(client):
    with patch("apps.analysis.views.predict_sms") as english_model:
        response = client.post(reverse("sms-check"), {
            "text": "Сәлем! Ертең сағат 15:00-де кездесейік."
        })
    assert response.status_code == 200
    english_model.assert_not_called()
    assert "словарь правил" in response.content.decode("utf-8")


def test_ru_suspicious_shows_reasons(client):
    with patch("apps.analysis.views.predict_sms") as english_model:
        response = client.post(reverse("sms-check"), {
            "text": "Срочно переведите 5000 ₸ и сообщите код подтверждения!"
        })
    assert response.status_code == 200
    english_model.assert_not_called()
    html = response.content.decode("utf-8")
    assert "Найдены признаки, требующие внимания" in html
    assert "Призыв к срочному действию" in html


def test_ru_no_invented_confidence():
    output = analyze_cyrillic_sms("Привет, встретимся завтра?")
    assert output["attention"] is False
    assert "probability" not in output


def test_english_still_uses_model(client):
    with patch("apps.analysis.views.predict_sms", return_value={"label": 1, "probability": 0.55}) as ml:
        response = client.post(reverse("sms-check"), {"text": "URGENT! Claim your prize."})
    assert response.status_code == 200
    ml.assert_called_once()
    assert "55.0%" in response.content.decode("utf-8")
