"""Create a local .env with a random secret. Never commit the output."""
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]
example = ROOT / ".env.example"
target = ROOT / ".env"
if target.exists():
    print("Файл .env уже существует — не изменяем его.")
else:
    content = example.read_text(encoding="utf-8")
    content = content.replace("DJANGO_SECRET_KEY=", f"DJANGO_SECRET_KEY={secrets.token_urlsafe(48)}", 1)
    target.write_text(content, encoding="utf-8")
    print("Создан .env с локальным случайным ключом. Не добавляйте его в Git!")
