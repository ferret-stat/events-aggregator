# Events Aggregator

Backend-сервис для агрегации и предоставления информации о мероприятиях. Получает данные из внешнего Events Provider API, сохраняет их в PostgreSQL и предоставляет REST API для просмотра мероприятий, проверки свободных мест, регистрации и отмены регистрации.

## Возможности

- Синхронизация мероприятий из внешнего API с поддержкой cursor pagination.
- Инкрементальная синхронизация с сохранением checkpoint.
- Upsert событий и площадок без дублирования записей.
- Автоматическая синхронизация по расписанию через APScheduler.
- Получение списка мероприятий с фильтрацией и пагинацией.
- Получение подробной информации о мероприятии.
- Получение свободных мест с TTL-кешированием.
- Регистрация участников и отмена регистрации.
- Обработка ошибок внешнего API и валидация входных данных.

## Технологический стек

| Категория    | Технологии                    |
| ------------ | ----------------------------- |
| Language     | Python 3.12                   |
| API          | FastAPI, Pydantic             |
| Database     | PostgreSQL                    |
| ORM          | SQLAlchemy 2.0 (Async)        |
| Migrations   | Alembic                       |
| HTTP Client  | HTTPX                         |
| Scheduling   | APScheduler                   |
| Testing      | Pytest, Pytest-Asyncio, HTTPX |
| Code Quality | Ruff                          |
| Environment  | uv                            |
| Deployment   | Docker, Docker Compose        |
| CI/CD        | GitHub Actions                |

## Архитектура

Проект построен на принципах Clean Architecture с разделением ответственности:

```text
app/
├── api/                 # REST API, routes, schemas, dependencies
├── application/         # Use Cases и бизнес-сценарии
├── domain/              # Entities, interfaces, repositories
├── infrastructure/      # PostgreSQL, SQLAlchemy, HTTP Client,
│                        # cache, scheduler
└── core/                # Configuration

migrations/              # Alembic migrations
tests/                   # Unit, integration и API tests
```

Используемые архитектурные подходы:

- Clean Architecture
- Repository Pattern
- Unit of Work
- Dependency Injection
- Asynchronous I/O

## API

Основные endpoints:

| Method | Endpoint                        | Описание                 |
| ------ | ------------------------------- | ------------------------ |
| GET    | `/api/events/`                  | Список мероприятий       |
| GET    | `/api/events/{event_id}`        | Информация о мероприятии |
| GET    | `/api/events/{event_id}/seats/` | Свободные места          |
| POST   | `/api/tickets/`                 | Регистрация участника    |
| DELETE | `/api/tickets/{ticket_id}`      | Отмена регистрации       |

Документация API после запуска:

- Swagger UI: `/docs`
- OpenAPI: `/openapi.json`

## Запуск проекта

### Требования

- Python 3.12+
- uv
- Docker и Docker Compose
- API Key внешнего Events Provider API

### 1. Клонирование и установка зависимостей

```bash
git clone https://github.com/ferret-stat/events-aggregator/actions
cd events-aggregator
uv sync
```

### 2. Настройка окружения

Создай `.env` в корне проекта:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/events
EXTERNAL_API_URL=https://events-provider.dev-2.python-labs.ru
EXTERNAL_API_KEY=your_api_key
```

Используй параметры PostgreSQL и дополнительные настройки из конфигурации проекта.

### 3. Миграции базы данных

```bash
uv run alembic upgrade head
```

### 4. Запуск приложения

```bash
uv run uvicorn app.main:app --reload
```

API будет доступно по адресу:

`http://localhost:8000`

### Запуск через Docker Compose

```bash
docker compose up --build
```

## Тестирование

Запуск всех тестов:

```bash
uv run pytest
```

Запуск с подробным выводом:

```bash
uv run pytest -v
```

Проверка качества кода:

```bash
uv run ruff check .
```

Автоматическое исправление Ruff:

```bash
uv run ruff check . --fix
```

## CI/CD

GitHub Actions используется для автоматизации проверок проекта, включая установку зависимостей, запуск тестов и проверку качества кода.

---

**Events Aggregator** — асинхронный backend-сервис с интеграцией внешнего API, автоматической синхронизацией данных и REST API для управления регистрациями на мероприятия.
