FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY setup.py requirements.txt ./

# 🔥 FORCE CPU TORCH (IMPORTANT)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install rest
RUN pip install --no-cache-dir -e .

# Clean cache
RUN rm -rf /root/.cache

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]