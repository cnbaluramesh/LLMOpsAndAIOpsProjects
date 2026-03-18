## Single-stage build using uv (optimized for CPU-only, no CUDA)
## Simpler approach - no multi-stage complexity
## Reduces image size from 16GB to ~1-2GB

FROM python:3.12-slim

# Install build dependencies (needed for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv
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

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install CPU-only PyTorch FIRST (before uv sync)
# This prevents CUDA packages from being installed
RUN uv pip install --no-cache torch --index-url https://download.pytorch.org/whl/cpu

# Install all dependencies using uv sync
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Remove build tools after installation to save space
RUN apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the app - uv run automatically uses .venv
CMD ["uv", "run", "streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
