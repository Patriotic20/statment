FROM python:3.14-rc-slim

WORKDIR /app

# Контекст сборки — корень репозитория (требование Railway для монорепо).
COPY client-bot/pyproject.toml client-bot/uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

COPY client-bot/ .

CMD ["uv", "run", "python", "main.py"]
