FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY requirements.txt /app/requirements.txt
RUN pip install --prefix=/install --no-cache-dir -r /app/requirements.txt

FROM python:3.10-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN adduser --disabled-password --gecos '' oratio
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy app
COPY . /app
RUN chown -R oratio:oratio /app

USER oratio
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
