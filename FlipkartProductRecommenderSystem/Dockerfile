FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

# ✅ Fix here
COPY setup.py requirements.txt ./

RUN pip install --no-cache-dir -e .

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]