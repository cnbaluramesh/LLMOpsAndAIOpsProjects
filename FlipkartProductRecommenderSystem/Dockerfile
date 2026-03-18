FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copy only dependency files first
COPY setup.py ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Now copy only app code
COPY app.py ./
COPY src/ ./src/

EXPOSE 5000

CMD ["python", "app.py"]