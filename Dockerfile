# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --prefix=/install .

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r truenas && useradd -r -g truenas truenas

# Copy application
COPY src/ ./src/

# Set ownership
RUN chown -R truenas:truenas /app

USER truenas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import truenas_mcp; print('OK')" || exit 1

ENTRYPOINT ["truenas-mcp"]