FROM python:3.12-slim AS base
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app_dir

FROM base AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY . .

# Install dependencies and project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM base AS final
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual environment and project files from builder
COPY --from=builder /app_dir/.venv ./.venv
COPY --from=builder /app_dir .

# Set up the environment
ENV PATH="/app_dir/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app_dir/.venv"

CMD alembic upgrade head && \
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level error