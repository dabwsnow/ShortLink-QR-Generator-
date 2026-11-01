# ShortLink & QR Generator

Веб-сервис на Django для сокращения ссылок и мгновенной генерации QR-кодов с аналитикой переходов.

## Стек
- Python 3.12+ / Django 5+
- WhiteNoise (статика)
- qrcode + Pillow (генерация QR в памяти)
- PostgreSQL (Neon / Supabase) или SQLite (локально)
- Vercel Serverless

## Локальный запуск

```bash
cd django/final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## Деплой на Vercel

1. Создайте репозиторий на GitHub и загрузите содержимое папки `final`:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
git push -u origin main
```

2. В Vercel:
- Нажмите **Add New... -> Project** и импортируйте репозиторий.
- Framework Preset: **Other**.
- Root Directory: `./` (если репозиторий создан из папки `final`).
- В **Environment Variables** добавьте:
  - `SECRET_KEY` = любой случайный ключ
  - `DEBUG` = `False`
  - `DATABASE_URL` = строка подключения к PostgreSQL (например, бесплатный Neon.tech)

3. Нажмите **Deploy**.
