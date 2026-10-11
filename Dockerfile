FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt uvicorn pytest pytest-timeout playwright \
    && playwright install --with-deps chromium

COPY . .
RUN chmod +x deploy/start.sh

ENV PROVABLE_WORKSPACE=/data/workspace \
    PYTHONPATH=/app/backend \
    PYTHONUNBUFFERED=1
EXPOSE 8000 5174
CMD ["deploy/start.sh"]
