FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/defensa
COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic
COPY app ./app
RUN python -m pip install --no-cache-dir .

RUN addgroup --system defensa && adduser --system --ingroup defensa defensa \
    && mkdir -p /datos && chown defensa:defensa /datos
USER defensa

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
