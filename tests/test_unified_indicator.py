"""Проверяем единый статус без выдуманной ML-вероятности для RU/KK."""
from unittest.mock import patch
from django.urls import reverse


def test_shared_indicator_english(client):
    with patch("apps.analysis.views.predict_sms", return_value={"label": 0, "probability": 0.1019}):
        response = client.post(reverse("sms-check"), {"text": "Your order has been shipped."})
    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "Явных тревожных признаков не найдено" in html
    assert "10.19%" in html
    assert "Выявлено групп правил:" in html


def test_shared_indicator_russian_without_probability(client):
    with patch("apps.analysis.views.predict_sms") as model:
        response = client.post(reverse("sms-check"), {"text": "Привет! Встречаемся завтра в 18:00."})
    model.assert_not_called()
    html = response.content.decode("utf-8")
    assert "Явных тревожных признаков не найдено" in html
    assert "0 из 6" in html
    assert "вероятность спама не вычисляется" in html


def test_shared_indicator_kazakh_without_probability(client):
    with patch("apps.analysis.views.predict_sms") as model:
        response = client.post(reverse("sms-check"), {"text": "Сәлем! Ертең сағат 10:00-де кездесейік."})
    model.assert_not_called()
    html = response.content.decode("utf-8")
    assert "Казахский (предположительно)" in html
    assert "0 из 6" in html
    assert "Вероятность класса «спам» (ML)" not in html


def test_shared_indicator_russian_suspicious(client):
    response = client.post(reverse("sms-check"), {"text": "Срочно переведите деньги и сообщите код подтверждения!"})
    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "Требует внимания" in html
    assert "Найдены признаки, требующие внимания" in html
    assert "Вероятность класса «спам» (ML)" not in html
