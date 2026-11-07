# SMS Guard — задание №7: первая SMS ML-модель (baseline)

Это **дополнение** к уже существующему проекту после успешно завершённого задания №6. Не заменяйте весь проект. Для первого запуска нужны `data/processed/sms_clean.csv`, `data/processed/sms_split.json`, `ml/features.py`, `ml/preprocessing.py`, `ml/rules.py`.

1. Скопируйте `scripts/train_sms_baseline.py` в `scripts/`, `ml/baseline.py` в `ml/`, `tests/test_baseline.py` в `tests/`.
2. Из корня проекта запустите PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\train_sms_baseline.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -c "from ml.baseline import predict_sms; print(predict_sms('Your order has arrived today.'))"
.\.venv\Scripts\python.exe -c "from ml.baseline import predict_sms; print(predict_sms('URGENT! You won a prize. Claim now!'))"
```

3. Сохраните результат и график, проверьте метрики и ошибки. В отчёте обязательно кратко объясните **пять FN и пять FP**, если найдено столько. Если ошибок меньше пяти — укажите фактическое число. Это правило не повод менять предсказания.
4. Модель обучается **только на train** и оценивается **только на validation**; тестовую выборку не затрагиваем. Восьмое задание будет сравнивать три алгоритма и подбирать пороги. Нельзя на этом этапе оценивать модель на test, если хотите сохранить финальную независимую проверку.
5. `ml/artifacts/*.joblib` исключены `.gitignore`. Для рабочего прототипа файл модели должен быть на демонстрационной машине. Можно пересоздать его командой из шага 2. Если преподаватель требует модель в репозитории, добавьте свой локально обученный артефакт через `git add -f ml/artifacts/sms_baseline.joblib`, предварительно убедившись, что он не содержит персональных данных или секретов.
6. Не загружайте файлы `.joblib` из неизвестных источников: десериализация joblib небезопасна для недоверенных файлов.

Файлы, которые формируются при обучении:

- `ml/artifacts/sms_baseline.joblib`
- `docs/07_sms_baseline_metrics.json`
- `docs/figures/07_sms_baseline_confusion_matrix.png`

Коммит после проверки:

```powershell
git add scripts/train_sms_baseline.py ml/baseline.py tests/test_baseline.py docs/07_sms_baseline_metrics.json docs/figures/07_sms_baseline_confusion_matrix.png
git commit -m "task-07: baseline SMS classifier"
git push origin main
```
