# SMS Guard — минимальный веб-прототип после задания №7

Этот ZIP **добавляется** к существующему проекту `sms_guard`, в котором задания №1–6 уже выполнены и подготовлены `ml/baseline.py`, `ml/features.py` и `ml/artifacts/sms_baseline.joblib` после задания №7.

## Установка

1. Распакуйте ZIP и скопируйте файлы в корень своего проекта **с сохранением путей**.
2. При копировании заменятся только `config/urls.py`, `apps/analysis/views.py` и `templates/home.html`. Новые файлы: `templates/check_sms.html`, `tests/test_prototype.py`, `docs/07_baseline_analysis.md`.
3. Из корня проекта выполните:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe manage.py runserver
```

4. Откройте `http://127.0.0.1:8000/check/sms/` в браузере.
5. Проверьте два SMS:
   - `Your order has arrived today.`
   - `URGENT! You won a prize. Claim now!`

Ожидается динамическое вычисление вероятностей из `.joblib` (не фиксированные значения). В текущем окружении пользователя ранее получено 0.0818 и 0.55 соответственно; после повторного обучения значения могут измениться.

## Особенности и ограничения

- Отправка осуществляется обычной POST-формой с CSRF-токеном (страница перезагружается). JSON API появится позже.
- Есть проверки на пустой текст и длину более 1000 символов.
- Ввод экранируется Django; ссылки в тексте не превращаются в кликабельные.
- SMS в базу данных не записываются, сетевые запросы к ссылкам не выполняются.
- Нет авторизации, лимита запросов, отдельной URL-модели или Risk Score: это **только учебный прототип**.
- При отсутствии модели возвращается страница с понятной ошибкой и статусом HTTP 503.
- Качество классификации не подтверждено для русского и казахского языков.
- Обученную модель joblib загружайте только из собственного доверенного файла: формат небезопасен для посторонних артефактов.

## Сохранение в GitHub после проверки

```powershell
git status
git add config/urls.py apps/analysis/views.py templates/home.html templates/check_sms.html tests/test_prototype.py docs/07_baseline_analysis.md
git commit -m "prototype: SMS checking web interface"
git push origin main
```

Отдельный коммит `task-07: baseline SMS classifier` желательно сделать перед этим коммитом, если он ещё не создан.
