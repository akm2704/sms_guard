# SMS Guard — задание №2

Стартовый каркас интеллектуальной системы анализа SMS и URL. Выполнен по пункту **«Задание 2. Подготовка структуры проекта»** из ТЗ. Это **не** готовый классификатор: ML-модели и защищённые пользовательские функции будут добавлены в следующих заданиях.

## Запуск на Windows (PowerShell, из каталога `sms_guard`)

Если Python 3.11 не установлен, используйте установленную версию Python 3.11+ (`py -3.12`, `py -3.13` и т. д.). **Активация виртуальной среды не требуется**: команды используют `.venv\Scripts\python.exe` напрямую.

```powershell
cd sms_guard
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\make_env.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Проверка в браузере:
- Главная: `http://127.0.0.1:8000/` — страница «SMS Guard запущен».
- Статус: `http://127.0.0.1:8000/api/v1/health/` — JSON `{ "status": "ok" }`.

Если `py -3.11` не работает, посмотрите версии командой `py -0p`, затем подставьте установленную версию 3.11+. При необходимости используйте `python -m venv .venv`.

Если PowerShell сообщает об ограничении выполнения сценариев (`Activate.ps1`), **ничего менять не нужно**: приведённые команды не требуют активации.

## Проверки

Из папки проекта:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe manage.py check
```

Ожидается: три простых теста проходят, проверка Django сообщает, что системных ошибок нет. Если пакеты ещё не установлены, сначала запустите `pip install -r requirements.txt`.

## Git (после проверки)

```powershell
git init
git add .
git status
git commit -m "task-02: project structure"
```

Убедитесь, что `.env` **не отображается** в `git status`, а исходные датасеты и модели не коммитятся.

## Структура

- `config/` — настройки Django, URL-маршруты, ASGI/WSGI.
- `apps/accounts/` — учётные записи (пока каркас).
- `apps/analysis/` — обработка проверок (пока health-check).
- `apps/dashboard/` — статистика (пока каркас).
- `ml/` — код ML, признаки, risk (в последующих заданиях).
- `data/raw/`, `data/processed/` — исходные и обработанные датасеты.
- `docs/` — документация задания 1 и будущих этапов.
- `templates/`, `static/` — главная страница и базовые стили.
- `logs/` — лог с ротацией (до 1 МиБ × 5 резервных копий).
- `tests/` — тесты.
- `notebooks/` — Jupyter-исследования.

## Важные условия

- Секретный ключ создаётся локально командой `scripts/make_env.py` и **не входит** в архив и Git.
- Для разработки используется SQLite. PostgreSQL добавим при демонстрационной сборке, если требуется преподавателем.
- `DJANGO_DEBUG=True` — только для локального запуска; при демонстрации/развёртывании установите `False`, настройте HTTPS и `DJANGO_ALLOWED_HOSTS`.
- Bootstrap загружается через CDN; если нет интернета, интерфейс отобразится без Bootstrap-стилей.
