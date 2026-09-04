FROM python:3.14-rc-slim

WORKDIR /app

# Контекст сборки — корень репозитория (требование Railway для монорепо),
# поэтому пути указываются от него.
COPY backend/pyproject.toml backend/uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

COPY backend/ .

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
