# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy source first so pip install includes the package
COPY pyproject.toml README.md src/ ./

# Install Python dependencies (includes truenas_mcp package)
RUN pip install --no-cache-dir --prefix=/install .

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages (includes truenas_mcp)
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r truenas && useradd -r -g truenas truenas

# Set ownership
RUN chown -R truenas:truenas /app

USER truenas

ENTRYPOINT ["truenas-mcp"]