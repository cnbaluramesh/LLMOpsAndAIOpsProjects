# Base image
FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip tools (IMPORTANT for dependency resolution)
RUN pip install --upgrade pip setuptools wheel

# Copy only dependency files first (better caching)
COPY setup.py pyproject.toml requirements.txt* ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy rest of the application
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]