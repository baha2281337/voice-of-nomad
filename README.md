# Голос колледжа

Самостоятельная платформа обратной связи для Nomad College. Проект разрабатывается поэтапно.

## Стек

- Django 5.2 LTS и Django REST Framework
- PostgreSQL в Docker Compose; SQLite для локального запуска без Docker
- OpenAPI 3, Swagger UI и ReDoc на базе `drf-spectacular`
- Django templates для начального веб-интерфейса

## Локальный запуск без Docker

1. Создайте и активируйте виртуальное окружение Python.
2. Установите зависимости: `python -m pip install -r requirements.txt`.
3. Скопируйте `.env.example` в `.env` и задайте случайный `SECRET_KEY`.
4. Выполните `python manage.py check`, затем `python manage.py runserver`.

## Запуск Docker Compose

1. Установите и запустите Docker Desktop.
2. Скопируйте `.env.example` в `.env` и задайте случайные значения `SECRET_KEY` и `DB_PASSWORD`.
3. Запустите приложение и PostgreSQL: `docker compose up --build`.
4. Откройте `http://localhost:8000`.

Compose применяет миграции Django при старте приложения. Данные PostgreSQL сохраняются в именованном Docker-томе. Остановить контейнеры, сохранив базу, можно командой `docker compose down`.

Compose-конфигурация предназначена для локальной разработки и публикует порт только на localhost. Для публичного развёртывания нужны отдельные настройки production-сервера, HTTPS и секретов.

## API-документация

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI-схема: `http://localhost:8000/api/schema/`
На текущем этапе у API ещё нет пользовательских маршрутов, поэтому документация пока содержит только схему и метаданные. Маршруты будут появляться вместе с последующими этапами функциональной разработки.

Не добавляйте `.env`, реальные секреты или локальные данные базы в Git.
