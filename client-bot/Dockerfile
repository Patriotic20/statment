FROM python:3.14-rc-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "python", "main.py"]
