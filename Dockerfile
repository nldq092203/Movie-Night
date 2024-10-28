# Stage 1: Build dependencies
FROM python:3.9-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim
WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "movienight.wsgi:application"]