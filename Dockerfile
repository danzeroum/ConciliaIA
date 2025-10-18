# BuildToValue v7.0 - Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="BuildToValue Team <team@buildtovalue.com>"
LABEL version="7.0"
LABEL description="BuildToValue v7 - AI Squad for Software Development"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p \
    .buildtovalue/config \
    .buildtovalue/ledger/decisions \
    .buildtovalue/learning/rag-index \
    logs

# Make scripts executable
RUN find scripts -type f -name "*.sh" -exec chmod +x {} +

# Expose application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/v7/health || exit 1

# Default command
CMD ["python", "src/main.py"]
