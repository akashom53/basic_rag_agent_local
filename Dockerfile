# Build stage with dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# # Install build dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# Optimized:
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages with BuildKit cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# # Copy application code
# COPY app/ ./app/
# COPY schema/ ./schema/

# # Create non-root user
# RUN useradd --create-home --shell /bin/bash app && \
#     chown -R app:app /app
# USER app


# Optimized:
RUN useradd --create-home --shell /bin/bash app
COPY --chown=app:app app/ ./app/
COPY --chown=app:app schema/ ./schema/
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
