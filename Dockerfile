# =============================================================================
# InscribeVerse Python Server Dockerfile
# Multi-stage build for development and production environments
# =============================================================================

# =============================================================================
# Base Stage - Common dependencies and setup
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        gcc \
        g++ \
        git \
        libmagic1 \
        libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install watchdog

# Create directories
RUN mkdir -p /app/logs /app/uploads /app/static \
    && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base as production

# Install production server
RUN pip install gunicorn

# Create directories with proper permissions
RUN mkdir -p /app/logs /app/uploads /app/static \
    && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Remove development files
RUN rm -rf \
    .git \
    .gitignore \
    .dockerignore \
    Dockerfile* \
    docker-compose* \
    README.md \
    /app/tests \
    /app/docs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with Gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

# =============================================================================
# Testing Stage (for CI/CD)
# =============================================================================
FROM development as testing

# Install testing dependencies (already included in requirements.txt)
USER root

# Install additional testing tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Copy test configuration
COPY --chown=appuser:appuser ./tests ./tests
COPY --chown=appuser:appuser pytest.ini .
COPY --chown=appuser:appuser .coveragerc .

# Default command for testing
CMD ["pytest", "--cov=app", "--cov-report=term-missing", "--cov-report=html"]

# =============================================================================
# Build Info Labels
# =============================================================================
LABEL maintainer="InscribeVerse Team" \
      version="1.0.0" \
      description="InscribeVerse Meta-System API Server" \
      org.opencontainers.image.source="https://github.com/your-org/inscribeverse" \
      org.opencontainers.image.documentation="https://docs.inscribeverse.com" \
      org.opencontainers.image.licenses="MIT" 