FROM python:3.14-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_SYSTEM_PYTHON=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY ./pyproject.toml ./uv.lock .

RUN uv sync --frozen --no-dev --no-cache

COPY ./app .

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14 /usr/local/lib/python3.14
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN chmod +x ./prestart.sh ./run

#ENTRYPOINT ["./prestart.sh"]
CMD ["./run"]
