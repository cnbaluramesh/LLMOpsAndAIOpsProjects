## Parent image - using Python 3.12 (required by project)
FROM python:3.12-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Set UV_CACHE_DIR to leverage Docker layer caching
    UV_CACHE_DIR=/root/.cache/uv \
    # Ensure uv uses the cache directory
    UV_LINK_MODE=copy

## Work directory inside the docker container
WORKDIR /app

## Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

## Install uv - faster Python package installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

## Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

## Install dependencies using uv sync
# --frozen: Use uv.lock without updating it (reproducible builds)
# --no-dev: Skip development dependencies (smaller production image)
RUN uv sync --frozen --no-dev

## Copy application code
COPY . .

## Make sure the app can find the modules
ENV PYTHONPATH=/app

## Expose the Streamlit port
EXPOSE 8501

## Run the app using uv to ensure correct environment
# Using uv run ensures we use the virtual environment created by uv
CMD ["uv", "run", "streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
