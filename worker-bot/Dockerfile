FROM python:3.14-rc-slim

WORKDIR /app

# Контекст сборки — корень репозитория (требование Railway для монорепо).
COPY worker-bot/pyproject.toml worker-bot/uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

COPY worker-bot/ .

CMD ["uv", "run", "python", "main.py"]
