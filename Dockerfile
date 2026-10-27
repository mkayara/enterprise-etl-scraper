FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install-deps chromium \
    && playwright install chromium

COPY . .

EXPOSE 8501 8000

CMD ["streamlit", "run", "app/ui/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
