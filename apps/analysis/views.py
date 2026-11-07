"""Health endpoint and the educational SMS prototype (tasks 1–7).

English SMS: trained ML baseline.
Cyrillic SMS: transparent rules, WITHOUT an invented ML probability.
"""
import re

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from ml.baseline import predict_sms
from ml.cyrillic_rules import analyze_cyrillic_sms, GROUP_TITLES
from ml.rules import detect_se_groups


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


@require_http_methods(["GET", "POST"])
def sms_check(request):
    context = {"text": ""}
    status = 200

    if request.method == "POST":
        text = request.POST.get("text", "")
        context["text"] = text

        if not text.strip():
            context["error"] = "Введите текст SMS для проверки."
            status = 400
        elif len(text) > 1000:
            context["error"] = "Текст SMS не должен превышать 1000 символов."
            status = 400
        elif re.search(r"[\u0400-\u052f]", text):
            # The original EN model cannot honestly produce reliable scores
            # for Cyrillic. Do not pass such texts to its predict_proba.
            analysis = analyze_cyrillic_sms(text)
            groups = detect_se_groups(text)
            kazakh_letters = set("әғқңөұүһі")
            is_kazakh = any(ch in kazakh_letters for ch in text.lower())
            context.update({
                "language": "kk" if is_kazakh else "ru",
                "language_label": "Казахский (предположительно)" if is_kazakh else "Русский (предположительно)",
                "indicator_alert": bool(analysis["attention"]),
                "indicator_title": "Требует внимания" if analysis["attention"] else "Явных тревожных признаков не найдено",
                "se_group_count": len(groups),
                "se_group_reasons": [GROUP_TITLES.get(g, g) for g in groups],
                "checked": True,
                "analysis_mode": "rules_cyrillic",
                "rules_alert": analysis["attention"],
                "reasons": analysis["reasons"],
            })
        else:
            try:
                result = predict_sms(text)
            except FileNotFoundError:
                context["error"] = (
                    "Файл обученной модели отсутствует. "
                    "Сначала запустите scripts/train_sms_baseline.py."
                )
                status = 503
            else:
                p = max(0.0, min(1.0, float(result["probability"])))
                groups = detect_se_groups(text)
                context.update({
                    "checked": True,
                    "analysis_mode": "ml_en",
                    "language": "en",
                    "language_label": "Английский (предположительно)",
                    "indicator_alert": result["label"] == 1,
                    "indicator_title": "Требует внимания" if result["label"] == 1 else "Явных тревожных признаков не найдено",
                    "se_group_count": len(groups),
                    "se_group_reasons": [GROUP_TITLES.get(g, g) for g in groups],
                    "is_spam": result["label"] == 1,
                    "probability_percent": round(p * 100, 2),
                })

    # Django auto-escapes all user-supplied SMS in the template.
    return render(request, "check_sms.html", context, status=status)
