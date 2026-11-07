"""Prototype page tests: protect UX and prevent the need to train during tests."""
from unittest.mock import patch

from django.urls import reverse


def test_sms_page_get(client):
    response = client.get(reverse("sms-check"))
    assert response.status_code == 200
    assert "Проверка SMS" in response.content.decode("utf-8")


def test_sms_page_empty_rejected(client):
    response = client.post(reverse("sms-check"), {"text": "   "})
    assert response.status_code == 400
    assert "Введите текст SMS" in response.content.decode("utf-8")


def test_sms_page_too_long_rejected(client):
    response = client.post(reverse("sms-check"), {"text": "a" * 1001})
    assert response.status_code == 400
    assert "1000 символов" in response.content.decode("utf-8")


def test_sms_page_result(client):
    with patch("apps.analysis.views.predict_sms", return_value={"label": 1, "probability": 0.55}):
        response = client.post(reverse("sms-check"), {"text": "URGENT! Claim your prize."})
    assert response.status_code == 200
    assert "55.0%" in response.content.decode("utf-8")
    assert "признаки спама" in response.content.decode("utf-8")


def test_sms_page_no_raw_html(client):
    malicious = "<script>alert(1)</script>"
    with patch("apps.analysis.views.predict_sms", return_value={"label": 0, "probability": 0.15}):
        response = client.post(reverse("sms-check"), {"text": malicious})
    html = response.content.decode("utf-8")
    assert response.status_code == 200
    assert "&lt;script&gt;" in html
    assert malicious not in html


def test_sms_page_model_missing(client):
    with patch("apps.analysis.views.predict_sms", side_effect=FileNotFoundError()):
        response = client.post(reverse("sms-check"), {"text": "Hello world!"})
    assert response.status_code == 503
    assert "модели отсутствует" in response.content.decode("utf-8")


def test_sms_page_warns_on_cyrillic(client):
    with patch("apps.analysis.views.predict_sms", return_value={"label": 0, "probability": 0.2}):
        response = client.post(reverse("sms-check"), {"text": "Привет, как дела?"})
    assert response.status_code == 200
    assert "надёжность такой оценки не подтверждена" in response.content.decode("utf-8")
