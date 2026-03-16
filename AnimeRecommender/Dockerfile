## Multi-stage build for smaller image size (CPU-only - no GPU)
## This Dockerfile prevents CUDA dependencies and reduces size from 16GB to ~1-2GB

## Stage 1: Builder
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install CPU-only PyTorch first (before other dependencies)
# This prevents CUDA packages from being installed
RUN uv pip install --no-cache --system torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
# UV_LINK_MODE=copy reduces image size
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev

## Stage 2: Runtime (much smaller)
FROM python:3.12-slim

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for running the app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Disable model caches to save space
    TRANSFORMERS_CACHE=/tmp/.cache \
    HF_HOME=/tmp/.cache \
    TORCH_HOME=/tmp/.torch

WORKDIR /app

# Copy virtual environment and python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the app
CMD ["uv", "run", "streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
