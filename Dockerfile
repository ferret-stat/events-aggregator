FROM python:3.12-slim

# Настройки Python и uv
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем production-зависимости
RUN uv sync --frozen --no-dev

# Добавляем виртуальное окружение в PATH
ENV PATH="/app/.venv/bin:$PATH"

# Копируем приложение
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

# Открываем порт
EXPOSE 8000

# Запуск миграций и приложения
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
