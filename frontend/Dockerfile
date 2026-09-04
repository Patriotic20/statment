FROM node:22-alpine AS builder

WORKDIR /app

# Контекст сборки — корень репозитория (требование Railway для монорепо).
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Конфиг — шаблон: nginx-образ подставит в него переменные окружения при старте.
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template

# Значения по умолчанию рассчитаны на локальный docker compose.
ENV PORT=80 \
    BACKEND_SCHEME=http \
    BACKEND_UPSTREAM=backend:8000 \
    NGINX_RESOLVER="127.0.0.11 ipv6=off"

EXPOSE 80
